# Distribuição de credenciais iniciais

1. Execute as migrações e o seed em um terminal administrativo.
2. Grave a saída em um diretório protegido ou volume temporário:

   ```bash
   python -m app.seed \
     --credentials-output /run/secrets/syncrohub-credenciais-iniciais.json
   ```

3. O script cria o arquivo com modo `0600` e falha se ele já existir.
4. Importe as credenciais em um cofre corporativo e distribua cada senha por
   um canal autenticado separado do email do usuário.
5. Remova o arquivo temporário após confirmar a importação no cofre.

Todas as senhas são aleatórias, têm 16 caracteres, são armazenadas com bcrypt
e 12 rounds e deixam `force_password_change=true`. O token obtido no primeiro
login fica restrito a `/auth/me` e `/auth/change-password` até a troca.

Nunca envie o arquivo em email, chat, ticket, commit ou artefato de CI.
