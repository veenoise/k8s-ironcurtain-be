pipeline {
    agent any
    
    environment {
        APP_NAME = "ironcurtain-be"
        HARBOR_PROJECT = "ironcurtain-be"
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                git url: 'https://github.com/veenoise/k8s-ironcurtain-be',
                    branch: 'main',
                    credentialsId: 'github_account'
            }
        }
        stage('Login to Harbor') {
            steps {
                withInfisical(configuration: [infisicalCredentialId: 'jenkins_universal_auth', infisicalEnvironmentSlug: 'dev', infisicalProjectSlug: 'global-harbor', infisicalUrl: 'https://infisical.sabihinmolang.eu.org'], infisicalSecrets: [infisicalSecret(includeImports: true, path: '/', secretValues: [[infisicalKey: 'HARBOR_EMAIL'], [infisicalKey: 'HARBOR_PASSWORD'], [infisicalKey: 'HARBOR_REGISTRY'], [infisicalKey: 'HARBOR_USERNAME']])]) {
                    sh '''
                        docker login -u ${HARBOR_USERNAME} -p ${HARBOR_PASSWORD} ${HARBOR_REGISTRY}
                    '''
                }
            }
        }
        stage('Build Docker') {
            steps {
                sh '''
                    docker build -t ${APP_NAME}:latest -t ${APP_NAME}:${BUILD_ID} .
                '''
            }
        }
        stage('Tag to Harbor') {
            steps {
                withInfisical(configuration: [infisicalCredentialId: 'jenkins_universal_auth', infisicalEnvironmentSlug: 'dev', infisicalProjectSlug: 'global-harbor', infisicalUrl: 'https://infisical.sabihinmolang.eu.org'], infisicalSecrets: [infisicalSecret(includeImports: true, path: '/', secretValues: [[infisicalKey: 'HARBOR_REGISTRY']])]) {
                    sh '''
                        docker tag ${APP_NAME}:${BUILD_ID} ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/${APP_NAME}:${BUILD_ID}
                        docker tag ${APP_NAME}:latest ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/${APP_NAME}:latest
                    '''
                }
            }
        }
        stage('Push to Harbor') {
            steps {
                withInfisical(configuration: [infisicalCredentialId: 'jenkins_universal_auth', infisicalEnvironmentSlug: 'dev', infisicalProjectSlug: 'global-harbor', infisicalUrl: 'https://infisical.sabihinmolang.eu.org'], infisicalSecrets: [infisicalSecret(includeImports: true, path: '/', secretValues: [[infisicalKey: 'HARBOR_REGISTRY']])]) {
                    sh '''
                        docker push ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/${APP_NAME}:${BUILD_ID}
                        docker push ${HARBOR_REGISTRY}/${HARBOR_PROJECT}/${APP_NAME}:latest
                    '''
                }
            }
        }
    }
    post {
        success {
            echo 'Pipeline Success!'
        }
        failure {
            echo 'Pipeline Failed!'
        }
        always {
            sh '''
                docker rmi $(docker image ls --format "{{.Repository}}:{{.Tag}}" | grep ${APP_NAME}) || true
                echo 'Deleted unused images!'
            '''
        }
    }
}
