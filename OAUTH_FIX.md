# 🔧 OAuth Common Issues & Fixes

## 1️⃣ "Google hasn't verified this app" Warning

### 😱 Tela que Aparece:
```
Google hasn't verified this app

The app is requesting access to sensitive info in your Google Account.
Until the developer (easycutdark@gmail.com) verifies this app with Google,
you shouldn't use it.

Continue only if you understand the risks and trust the developer.
```

### ✅ Isso é NORMAL e SEGURO!

**Por que aparece:**
- O app não passou pela verificação oficial do Google (demora 4-6 semanas)
- É o **seu próprio app** ou um app open-source que você confia
- Google mostra isso como precaução para apps não-verificados

**Como Continuar (É Seguro!):**
1. Clique em **"Advanced"** (ou "Hide Advanced") no canto inferior esquerdo
2. Vai aparecer um link: **"Go to EasyCut (unsafe)"**
3. **Clique nele**
4. Pronto! Vai continuar o fluxo OAuth normalmente

**Nota:** "unsafe" não significa que o app é malicioso. Significa apenas que não foi verificado pelo Google.

---

## 2️⃣ OAuth Error 403: access_denied

### Erro que Aparece:
```
EasyCut não concluiu o processo de verificação do Google. 
Ele está em fase de testes e só pode ser acessado por 
testadores aprovados pelo desenvolvedor.

Erro 403: access_denied
```

## 🎯 Solução:

O OAuth app está em **modo Testing**. Para funcionar, você precisa adicionar o email da conta Google que vai usar como "Test User".

### Passo a passo:

1. **Acesse o Google Cloud Console:**
   - https://console.cloud.google.com/

2. **Selecione o projeto:** `EasyCut` (ou `sunny-caldron-487419-e4`)

3. **Menu lateral → "OAuth consent screen"**

4. **Seção "Test users" → clique em "ADD USERS"**

5. **Digite seu email do Google** (ou da conta que vai usar no EasyCut)
   - Exemplo: `seuemail@gmail.com`

6. **Clique "SAVE"**

7. **Pronto!** Agora você pode clicar "Sync with YouTube" no EasyCut

---

## 🚀 Alternativa: Publicar o App (Recomendado para Distribuição)

Se você quer que QUALQUER pessoa possa usar o EasyCut sem adicionar email:

1. No "OAuth consent screen"
2. Clique em **"PUBLISH APP"**
3. Confirme

**Nota:** Não precisa passar por verificação do Google se você só usa scopes básicos como `youtube.readonly`.

---

## 📌 Por Que Esse Erro Acontece?

- Google coloca novos OAuth apps em "Testing" por padrão
- Em "Testing", apenas emails pré-aprovados podem autenticar
- É uma medida de segurança para apps em desenvolvimento
- Para uso público, precisa publicar o app

## ✅ Checklist:

- [ ] Adicionar email como Test User
- [ ] OU Publicar o app
- [ ] Testar "Sync with YouTube" novamente
- [ ] Clicar "Advanced" → "Go to EasyCut (unsafe)" quando aparecer a tela de verificação
- [ ] Deve funcionar! 🎉

---

## 3️⃣ Remover a Tela "Unverified App" (Para Lançamento Público)

Se você quer lançar o EasyCut para o público geral sem a tela de aviso:

### **Opção A: Submeter para Verificação do Google** ⭐ Recomendado

**Processo completo documentado em:** [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)

**Resumo:**
1. Criar Privacy Policy e Terms of Service ✅ (já feito!)
2. Fazer vídeo de demonstração do app
3. Preencher formulário no Google Cloud Console
4. Submeter para verificação
5. Aguardar 4-6 semanas
6. **Resultado:** Tela de aviso desaparece completamente!

**Documentos prontos:**
- ✅ [PRIVACY.md](PRIVACY.md) - Política de Privacidade
- ✅ [TERMS.md](TERMS.md) - Termos de Serviço
- ✅ [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) - Passo a passo completo

### **Opção B: Publicar sem Verificar** (Rápido mas não ideal)

**Resultado:**
- ✅ Remove erro 403 (access_denied)
- ⚠️ MANTÉM a tela "This app hasn't been verified"
- ⚠️ Users precisam clicar "Advanced" → "Continue"

**Como fazer:**
1. Google Cloud Console → OAuth consent screen
2. Status: "Testing" → Clique em **"PUBLISH APP"**
3. Confirme
4. Pronto!

**Desvantagem:** Usuários menos técnicos podem ter medo de continuar.

### **Opção C: Cada Usuário Cria Suas Credenciais** (Mais técnico)

**Resultado:**
- ✅ Cada usuário cria seu próprio OAuth app
- ✅ Sem tela de aviso (é o próprio app do usuário)
- ❌ Processo complicado para usuarios não-técnicos

**Documentação:** [OAUTH_SETUP.md](OAUTH_SETUP.md)

---

## 🎯 Recomendação para Lançamento

**Para uso pessoal:** Clique "Advanced" → "Continue" e pronto!

**Para lançamento público:** Siga o [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) e submeta para verificação oficial do Google.

**Timeline:**
- Preparação: ~1 hora
- Submissão: ~30 minutos  
- Revisão do Google: 4-6 semanas
- **Resultado:** App 100% profissional e verificado! ✅
