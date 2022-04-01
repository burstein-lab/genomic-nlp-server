# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

## Recommended IDE Setup

- [VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=johnsoncodehk.volar)

# Deployment

Followed these guides https://jonhnes.medium.com/vue-with-docker-since-creation-until-deployment-on-heroku-5b31c8f041a7
and https://cli.vuejs.org/guide/deployment.html#docker-nginx
in order to deploy vuejs+docker on heroku.

To deploy:

```bash
heroku login
heroku container:login
heroku container:push web -a gnlp-web
heroku container:release web -a gnlp-web
heroku open -a gnlp-web # Or go to https://gnlp-web.herokuapp.com/
heroku logs -a gnlp-web --tail
```

Initial Heroku setup:

```
heroku login
heroku container:login
heroku git:remote -a gnlp-web # Or create a new one with `heroku create`
heroku container:push web
heroku container:release web
heroku open
```

## Test locally

```bash
docker build . -t gnlp-web
docker run -it -e PORT=80 -p 8000:80 --rm gnlp-web
```
