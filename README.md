# wtf_scholar-web
Web application for Manuscript GEN

docker 部署
下载release中的镜像zip,
解压为前后端的tar
dockerfile

构建 Docker 镜像：
backend

docker build -t wtf-api-backend -f Backend/Dockerfile .

docker run -d -p 5001:5001 flask-api-app

————————————————————

frontend

docker build -t wtf-frontend-dev -f frontend/Dockerfile .

docker run -d -p 5173:5173 vue-frontend-dev




# frontend
# academic-writing-assistant

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

**npm run serve**

# backend

pip install -r requirements.txt
