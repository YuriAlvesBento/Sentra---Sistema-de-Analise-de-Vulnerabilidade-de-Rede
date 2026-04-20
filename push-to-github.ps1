# Script para fazer Push do SENTRA para GitHub automaticamente
# Use: .\push-to-github.ps1

param(
    [string]$GitHubUsername = "",
    [string]$RepositoryName = "sentra",
    [string]$RepositoryUrl = ""
)

Write-Host "🚀 SENTRA - GitHub Push Helper" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Se não tiver URL, pedir ao usuário
if (-not $RepositoryUrl) {
    $GitHubUsername = Read-Host "Digite seu username do GitHub"
    $RepositoryName = Read-Host "Digite o nome do repositório (padrão: sentra)"
    
    if ([string]::IsNullOrWhiteSpace($RepositoryName)) {
        $RepositoryName = "sentra"
    }
    
    $RepositoryUrl = "https://github.com/$GitHubUsername/$RepositoryName.git"
}

Write-Host ""
Write-Host "📝 Informações:" -ForegroundColor Yellow
Write-Host "   URL: $RepositoryUrl"
Write-Host "   Branch: main"
Write-Host ""

$confirm = Read-Host "Deseja continuar? (s/n)"

if ($confirm -ne 's' -and $confirm -ne 'S') {
    Write-Host "❌ Operação cancelada!" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "⏳ Configurando..." -ForegroundColor Blue

# Ir para a pasta do projeto
Push-Location "c:\Users\CLIENTE\Desktop\Sentra\Sentra"

try {
    # Renomear branch para main se necessário
    Write-Host "1️⃣  Renomeando branch..." -ForegroundColor Blue
    git branch -M main
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Branch renomeado para main" -ForegroundColor Green
    }
    
    # Adicionar remote
    Write-Host "2️⃣  Adicionando repositório remoto..." -ForegroundColor Blue
    git remote add origin $RepositoryUrl 2>$null
    if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 128) {
        Write-Host "   ✓ Remote configurado" -ForegroundColor Green
    }
    
    # Fazer push
    Write-Host "3️⃣  Fazendo push para GitHub..." -ForegroundColor Blue
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ SUCESSO! Seu projeto está no GitHub!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📍 Acesse em: $RepositoryUrl" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "✨ Pronto para apresentar aos professores!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Erro durante o push!" -ForegroundColor Red
        Write-Host "Certifique-se de que:" -ForegroundColor Yellow
        Write-Host "  - Você criou o repositório no GitHub"
        Write-Host "  - A URL está correta"
        Write-Host "  - Você tem um Personal Access Token configurado"
        Write-Host ""
        Write-Host "Veja GITHUB_PUSH_GUIDE.md para mais detalhes" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Erro: $_" -ForegroundColor Red
}
finally {
    Pop-Location
}

Write-Host ""
Read-Host "Pressione Enter para sair"
