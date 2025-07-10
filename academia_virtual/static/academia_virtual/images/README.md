# Imagens dos Professores - Academia Virtual

## Como adicionar fotos dos professores:

### 📋 **Especificações das Imagens:**
1. **Formatos aceitos**: JPG, PNG, WEBP
2. **Tamanho recomendado**: 200x200 pixels (quadrado)
3. **Nome do arquivo**: Use o padrão `professor-iniciais.extensão`

### 👥 **Professores atuais e seus arquivos:**
- `professor-MJ.webp` ✅ - Maria José (IMPLEMENTADO)
- `professor-as.jpg` - André Silva 
- `professor-lr.jpg` - Lucia Rodrigues
- `professor-cf.jpg` - Carlos Ferreira

## 🎯 **Como implementar as imagens:**

### **1. Cards dos Professores (Seção principal):**

Substitua as iniciais (ex: AS) por:

```html
<div class="professor-avatar">
    <img src="{% static 'academia_virtual/images/professor-as.jpg' %}" alt="André Silva">
</div>
```

### **2. Avatares Flutuantes (Decorativos):**

Para adicionar imagem a um avatar flutuante:

```html
<!-- Antes (só texto): -->
<div class="floating-avatar text-only">AS</div>

<!-- Depois (com imagem): -->
<div class="floating-avatar with-image">
    <img src="{% static 'academia_virtual/images/professor-as.jpg' %}" alt="André Silva">
    AS
</div>
```

**Classes importantes:**
- `with-image`: Para avatares com foto (esconde o texto)
- `text-only`: Para avatares só com iniciais

## 📊 **Status atual:**

### Cards dos Professores:
- ✅ Maria José: Imagem implementada
- ⏳ André Silva: Aguardando imagem
- ⏳ Lucia Rodrigues: Aguardando imagem  
- ⏳ Carlos Ferreira: Aguardando imagem

### Avatares Flutuantes:
- ✅ Avatar 1 (MJ): Imagem implementada
- ⏳ Avatar 2 (AS): Só iniciais
- ⏳ Avatar 3 (LR): Só iniciais
- ⏳ Avatar 4 (CF): Só iniciais

## 💡 **Dicas importantes:**
- Use a mesma imagem para o card e o avatar flutuante
- Evite nomes com espaços ou caracteres especiais
- Formatos WEBP são mais eficientes para web
- Teste sempre após adicionar uma nova imagem
- As imagens devem ter boa qualidade e fundo neutro
