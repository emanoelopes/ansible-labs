# Definir-ImagensPerfil.ps1
# Script para associar imagens de perfil a usuários locais no Windows 11 via SID

$Usuarios = @("Suporte", "Bolsista", "Aluno")
$PastaOrigem = "C:\Tecnodocencia\Imagens"

foreach ($User in $Usuarios) {
    # Define o caminho da imagem de origem baseado no nome do usuário (em minúsculas)
    $NomeArquivo = "perfil_$($User.ToLower()).png"
    $CaminhoImagem = Join-Path $PastaOrigem $NomeArquivo

    if (-Not (Test-Path $CaminhoImagem)) {
        Write-Warning "Imagem $CaminhoImagem não encontrada. Pulando usuário $User."
        continue
    }

    try {
        # Obtém o SID do usuário local
        $NTAccount = New-Object System.Security.Principal.NTAccount($User)
        $SID = $NTAccount.Translate([System.Security.Principal.SecurityIdentifier]).Value
    } catch {
        Write-Warning "Usuário $User não encontrado no sistema. Pulando."
        continue
    }

    # Diretório público onde o Windows armazena as imagens de conta baseadas no SID
    $PastaConta = "C:\Users\Public\AccountPictures\$SID"
    
    if (-Not (Test-Path $PastaConta)) {
        New-Item -Path $PastaConta -ItemType Directory -Force | Out-Null
    }

    # Copia a imagem para o diretório do SID (O Windows aceita PNG apesar de as vezes usar extensões diferentes internamente)
    $ImagemDestino = Join-Path $PastaConta "Image.png"
    Copy-Item -Path $CaminhoImagem -Destination $ImagemDestino -Force

    # Caminho do Registro onde o Windows mapeia as imagens da tela de login/menu iniciar
    $RegPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AccountPicture\Users\$SID"
    
    if (-Not (Test-Path $RegPath)) {
        New-Item -Path $RegPath -Force | Out-Null
    }

    # Injeta os valores apontando para a nova imagem. 
    # O Windows utiliza diferentes resoluções, mas apontar todas para a mesma imagem funciona perfeitamente.
    $Dimensoes = @("Image32", "Image40", "Image48", "Image96", "Image192", "Image240", "Image448")
    foreach ($Dimensao in $Dimensoes) {
        Set-ItemProperty -Path $RegPath -Name $Dimensao -Value $ImagemDestino -Force
    }

    Write-Output "Imagem de perfil configurada com sucesso para o usuário $User ($SID)."
}