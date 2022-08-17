FROM node:lts as build-stage
WORKDIR /app
COPY . .
RUN yarn install
RUN yarn build

FROM nginx:1.15.7-alpine as production-stage
COPY default.conf /etc/nginx/conf.d/
COPY --from=build-stage /app/dist/ /usr/share/nginx/html/
# To Heroku you can't expose a port
# EXPOSE 80
# To Heroku you need set port from env $PORT
CMD sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'