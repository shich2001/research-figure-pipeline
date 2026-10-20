param(
    [Parameter(Mandatory=$true)][string]$SpecPath,
    [Parameter(Mandatory=$true)][string]$OutputStem,
    [string]$Python='python',
    [string]$Font='Microsoft YaHei'
)
$ErrorActionPreference='Stop'
[Threading.Thread]::CurrentThread.CurrentCulture=[Globalization.CultureInfo]::InvariantCulture
$SpecPath=(Resolve-Path -LiteralPath $SpecPath).Path
$assetRoot=Split-Path $SpecPath -Parent
$stem=$ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputStem)
$out=Split-Path $stem -Parent
if(-not (Test-Path -LiteralPath $out -PathType Container)){throw 'Output directory must already exist.'}
foreach($ext in @('.vsdx','.png','.svg','.pdf')){
    if(Test-Path -LiteralPath ($stem+$ext)){throw "Refusing existing output: $stem$ext. Use a new output stem."}
}
& $Python (Join-Path $PSScriptRoot 'validate_editability.py') $SpecPath
if($LASTEXITCODE -ne 0){throw 'Spec validation failed before Visio was changed.'}
$spec=Get-Content -LiteralPath $SpecPath -Raw -Encoding UTF8 | ConvertFrom-Json
$scale=[double]$spec.page.mm_per_px / 25.4
$pageH=[double]$spec.page.height_px
if($Font.Contains('"')){throw 'Font must not contain quotes.'}
try {$visio=[Runtime.InteropServices.Marshal]::GetActiveObject('Visio.Application')}
catch {$visio=New-Object -ComObject Visio.Application}
$visio.Visible=$true
$target=$stem+'.vsdx'
# Always create a new document: never clear an existing user's page.
$doc=$visio.Documents.Add('')
$page=$doc.Pages.Item(1)
$page.Name='Research Figure'
$page.PageSheet.CellsU('PageWidth').FormulaU=("$([double]$spec.page.width_px*$scale) in")
$page.PageSheet.CellsU('PageHeight').FormulaU=("$($pageH*$scale) in")
function C([string]$hex) {
    return ('RGB({0},{1},{2})' -f [Convert]::ToInt32($hex.Substring(1,2),16),[Convert]::ToInt32($hex.Substring(3,2),16),[Convert]::ToInt32($hex.Substring(5,2),16))
}
function Layer($shape,[string]$name) {
    $ly=$null
    foreach($item in $page.Layers){if($item.Name -eq $name){$ly=$item;break}}
    if($null -eq $ly){$ly=$page.Layers.Add($name)}
    $ly.Add($shape,0)
}
foreach($b in $spec.shapes) {
    $x1=$b.x*$scale;$y1=($pageH-$b.y-$b.h)*$scale
    $x2=($b.x+$b.w)*$scale;$y2=($pageH-$b.y)*$scale
    if($b.kind -eq 'ellipse'){$s=$page.DrawOval($x1,$y1,$x2,$y2)}
    else {$s=$page.DrawRectangle($x1,$y1,$x2,$y2);$s.CellsU('Rounding').FormulaU="$($b.radius*$scale) in"}
    $s.NameU=$b.id
    $s.CellsU('FillForegnd').FormulaU=C $b.fill
    $s.CellsU('FillPattern').FormulaU='1'
    if($b.line){$s.CellsU('LineColor').FormulaU=C $b.line;$s.CellsU('LineWeight').FormulaU='0.8 pt'}
    else {$s.CellsU('LinePattern').FormulaU='0'}
    Layer $s '背景与卡片'
}
foreach($m in $spec.icons) {
    $s=$page.Import((Join-Path $assetRoot $m.path))
    $s.NameU=$m.id
    $s.CellsU('Width').FormulaU="$([double]$m.w*$scale) in"
    $s.CellsU('Height').FormulaU="$([double]$m.h*$scale) in"
    $s.CellsU('PinX').FormulaU="$(($m.x+$m.w/2)*$scale) in"
    $s.CellsU('PinY').FormulaU="$(($pageH-$m.y-$m.h/2)*$scale) in"
    Layer $s '独立透明插画'
}
foreach($a in $spec.arrows) {
        $pts=$a.points
        for($i=0;$i -lt $pts.Count-1;$i++){
            $p=$pts[$i];$q=$pts[$i+1]
            $s=$page.DrawLine(($p[0]*$scale),(($pageH-$p[1])*$scale),($q[0]*$scale),(($pageH-$q[1])*$scale))
            $s.NameU="$($a.id)_$i"
            $s.CellsU('LineColor').FormulaU=C $a.color
            $s.CellsU('LineWeight').FormulaU="$($a.weight*$scale*72) pt"
            $s.CellsU('EndArrow').FormulaU='0'
            if($a.head -and $i -eq $pts.Count-2){$s.CellsU('EndArrow').FormulaU='5';$s.CellsU('EndArrowSize').FormulaU='0'}
            Layer $s '流程箭头'
        }
}
foreach($t in $spec.texts) {
    $s=$page.DrawRectangle(($t.x*$scale),(($pageH-$t.y-$t.h)*$scale),(($t.x+$t.w)*$scale),(($pageH-$t.y)*$scale))
    $s.NameU=$t.id;$s.Text=$t.text
    $s.CellsU('FillPattern').FormulaU='0';$s.CellsU('LinePattern').FormulaU='0'
    $s.CellsU('Char.Font').FormulaU=('FONT("{0}")' -f $Font)
    $s.CellsU('Char.AsianFont').FormulaU=('FONT("{0}")' -f $Font)
    $s.CellsU('Char.Size').FormulaU="$($t.size*$scale*72) pt"
    $s.CellsU('Char.Color').FormulaU=C $t.color
    $s.CellsU('Char.Style').FormulaU=$(if($t.bold){'1'}else{'0'})
    $s.CellsU('Para.HorzAlign').FormulaU=$(if($t.align -eq 'center'){'1'}elseif($t.align -eq 'right'){'2'}else{'0'})
    $s.CellsU('VerticalAlign').FormulaU='1'
    foreach($margin in @('LeftMargin','RightMargin','TopMargin','BottomMargin')){$s.CellsU($margin).FormulaU='0 in'}
    Layer $s '可编辑文字'
}
$doc.SaveAs($target)
# Keep full master aspect ratio, exporting the actual Visio page.
$visio.Settings.SetRasterExportResolution(3,240,240,0)
$visio.Settings.SetRasterExportSize(2,0,0,0)
$visio.Settings.RasterExportBackgroundColor=16777215
$page.Export(($stem+'.png'))
$page.Export(($stem+'.svg'))
$doc.ExportAsFixedFormat(1,($stem+'.pdf'),1,0)
$doc.Save()
Write-Output "Created $target"
Write-Output "Independent Visio objects: $($page.Shapes.Count)"
