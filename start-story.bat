@echo off
rem Double-click to open the story site. Keep this window open while watching; close it to stop.
cd /d "%~dp0"
echo Starting story site at http://localhost:8000 ...
echo Keep this window open. Close it when you are done.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$root=(Get-Location).Path; $l=New-Object Net.HttpListener; $l.Prefixes.Add('http://localhost:8000/'); try{$l.Start()}catch{Start-Process 'http://localhost:8000/index.html'; exit}; Start-Process 'http://localhost:8000/index.html'; $types=@{'.html'='text/html; charset=utf-8';'.json'='application/json; charset=utf-8';'.js'='text/javascript; charset=utf-8';'.css'='text/css; charset=utf-8';'.png'='image/png';'.jpg'='image/jpeg'}; while($l.IsListening){ $c=$l.GetContext(); $p=[Uri]::UnescapeDataString($c.Request.Url.AbsolutePath.TrimStart('/')); if($p -eq ''){$p='index.html'}; $f=[IO.Path]::GetFullPath((Join-Path $root $p)); if($f.StartsWith($root) -and (Test-Path -LiteralPath $f -PathType Leaf)){ $b=[IO.File]::ReadAllBytes($f); $ext=[IO.Path]::GetExtension($f).ToLower(); if($types.ContainsKey($ext)){$c.Response.ContentType=$types[$ext]}; $c.Response.ContentLength64=$b.Length; $c.Response.OutputStream.Write($b,0,$b.Length) } else { $c.Response.StatusCode=404 }; $c.Response.Close() }"
