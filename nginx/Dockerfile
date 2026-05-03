FROM nginx:alpine

# Instalar openssl para gerar certificado autoassinado
RUN apk add --no-cache openssl

# Criar diretório para certificados SSL
RUN mkdir -p /etc/nginx/ssl

# Gerar certificado autoassinado
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=BR/ST=Estado/L=Cidade/O=Grupo2/CN=localhost"

# Remover configuração padrão
RUN rm /etc/nginx/conf.d/default.conf

# Copiar configuração customizada
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar arquivos estáticos do frontend
COPY html/ /usr/share/nginx/html/

EXPOSE 8080 8443
