pipeline {
    agent any
    
    environment {
        APP_NAME = "k8s-ironcurtain-be"
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                git url: 'https://github.com/veenoise/k8s-ironcurtain-be',
                    branch: 'main',
                    credentialsId: 'github_account'
            }
        }
        stage('Login to Quay') {
            steps {
                withInfisical(configuration: [infisicalCredentialId: 'jenkins_universal_auth', infisicalEnvironmentSlug: 'dev', infisicalProjectSlug: 'global-quay', infisicalUrl: 'https://infisical.sabihinmolang.eu.org'], infisicalSecrets: [infisicalSecret(includeImports: true, path: '/', secretValues: [[infisicalKey: 'QUAY_PASSWORD'], [infisicalKey: 'QUAY_HOSTNAME'], [infisicalKey: 'QUAY_USERNAME']])]) {
                    sh '''
                        docker login -u ${QUAY_USERNAME} -p ${QUAY_PASSWORD} ${QUAY_HOSTNAME}
                    '''
                }
            }
        }
        stage('Build Docker') {
            steps {
                sh '''
                    docker build -t ${APP_NAME}:latest .
                '''
            }
        }
        stage('Tag to Harbor') {
            steps {
                withInfisical(configuration: [infisicalCredentialId: 'jenkins_universal_auth', infisicalEnvironmentSlug: 'dev', infisicalProjectSlug: 'global-quay', infisicalUrl: 'https://infisical.sabihinmolang.eu.org'], infisicalSecrets: [infisicalSecret(includeImports: true, path: '/', secretValues: [[infisicalKey: 'QUAY_PASSWORD'], [infisicalKey: 'QUAY_HOSTNAME'], [infisicalKey: 'QUAY_USERNAME']])]) {
                    sh '''
                        docker tag ${APP_NAME}:latest ${QUAY_HOSTNAME}/${QUAY_USERNAME}/${APP_NAME}:latest
                    '''
                }
            }
        }
        stage('Push to Harbor') {
            steps {
                withInfisical(configuration: [infisicalCredentialId: 'jenkins_universal_auth', infisicalEnvironmentSlug: 'dev', infisicalProjectSlug: 'global-quay', infisicalUrl: 'https://infisical.sabihinmolang.eu.org'], infisicalSecrets: [infisicalSecret(includeImports: true, path: '/', secretValues: [[infisicalKey: 'QUAY_PASSWORD'], [infisicalKey: 'QUAY_HOSTNAME'], [infisicalKey: 'QUAY_USERNAME']])]) {
                    sh '''

                        docker push ${QUAY_HOSTNAME}/${QUAY_USERNAME}/${APP_NAME}:latest
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
