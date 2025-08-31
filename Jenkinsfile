pipeline {
    agent any
    environment {
        DOCKER_REGISTRY = 'crpi-wtmypn5u0qgeinul.cn-beijing.personal.cr.aliyuncs.com'
        DOCKER_NAMESPACE = 'caijg-dev'
        DOCKER_REPO = 'hackathon_backend'
        DOCKER_REPO2 = 'hackathon_frontend'
        VERSION = "v0.0.1"
        USERNAME = ""
        PASSWORD = ""
    }

    stages {
        stage('构建后端镜像') {
            steps {
                script {
                    echo '=== 开始构建后端镜像 ==='
                    sh "docker build -t ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/${DOCKER_REPO}:${VERSION} -f Dockerfile ."
                }
            }
        }

        stage('构建前端镜像') {
            steps {
                script {
                    echo '=== 开始构建前端镜像 ==='
                    sh "docker build -t ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/${DOCKER_REPO2}:${VERSION} -f external/aiqtoolkit-opensource-ui/Dockerfile external/aiqtoolkit-opensource-ui"
                }
            }
        }

        stage('发布到阿里云仓库') {
            steps {
                script {
                    echo '=== 开始发布到阿里云仓库 ==='
                    sh "docker login -u=${USERNAME} -p=${PASSWORD} ${DOCKER_REGISTRY}"
                    sh "docker push ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/${DOCKER_REPO}:${VERSION}"
                    sh "docker push ${DOCKER_REGISTRY}/${DOCKER_NAMESPACE}/${DOCKER_REPO2}:${VERSION}"
                    sh "docker logout ${DOCKER_REGISTRY}"
                }
            }
        }

        stage('清理资源') {
            steps {
                script {
                    echo '=== 开始清理资源 ==='
                    sh 'docker system prune -f'
                }
            }
        }
    }

    post {
        success {
            echo '=== 构建和部署成功！==='
        }
        failure {
            echo '=== 构建或部署失败！==='
        }
    }
}