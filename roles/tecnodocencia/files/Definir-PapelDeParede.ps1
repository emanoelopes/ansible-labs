# Definir-PapelDeParede.ps1
# Aplica o papel de parede padrão da tecnodocência a TODOS os usuários locais.
#
# A política de papel de parede do Windows é lida por usuário (HKCU), não de
# HKLM. Por isso gravamos no perfil Default (contas ainda sem perfil) e no
# registro de cada perfil existente (carregando o NTUSER.DAT se o usuário
# não estiver logado). O efeito aparece no próximo logon de cada usuário.

$ErrorActionPreference = 'Stop'
$Imagem = 'C:\Tecnodocencia\Imagens\papel_de_parede_tecnodocencia.jpeg'
$Sub = 'Software\Microsoft\Windows\CurrentVersion\Policies\System'

if (-not (Test-Path $Imagem)) { throw "Imagem $Imagem não encontrada." }

function Set-PapelDeParede($Raiz) {
    $chave = "$Raiz\$Sub"
    New-Item -Path $chave -Force | Out-Null
    Set-ItemProperty -Path $chave -Name Wallpaper -Value $Imagem
    Set-ItemProperty -Path $chave -Name WallpaperStyle -Value '2'
}

function Set-ComHive($Nome, $Arquivo) {
    reg.exe load "HKU\$Nome" $Arquivo | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Falha ao carregar $Arquivo" }
    try { Set-PapelDeParede "Registry::HKEY_USERS\$Nome" }
    finally {
        [gc]::Collect(); [gc]::WaitForPendingFinalizers()
        reg.exe unload "HKU\$Nome" | Out-Null
    }
}

# Perfil padrão: vale para contas que ainda não fizeram logon.
Set-ComHive 'TMP_Default' 'C:\Users\Default\NTUSER.DAT'
Write-Output 'Perfil Default: ok'

# Perfis existentes.
Get-ChildItem 'C:\Users' -Directory -Force |
    Where-Object { $_.Name -notin 'Default', 'Public', 'All Users', 'Default User' } |
    ForEach-Object {
        $hive = Join-Path $_.FullName 'NTUSER.DAT'
        if (-not (Test-Path -LiteralPath $hive)) { return }
        try {
            $sid = (New-Object System.Security.Principal.NTAccount($_.Name)).Translate(
                [System.Security.Principal.SecurityIdentifier]).Value
        } catch { Write-Warning "$($_.Name): sem conta local, pulando."; return }
        if (Test-Path "Registry::HKEY_USERS\$sid") {
            Set-PapelDeParede "Registry::HKEY_USERS\$sid"   # logado: hive já carregado
        } else {
            Set-ComHive "TMP_$($_.Name)" $hive
        }
        Write-Output "$($_.Name): ok"
    }
