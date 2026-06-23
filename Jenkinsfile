pipeline {
    agent any
    
    environment {
        APP_NAME = "k8s-ironcurtain-be"
    }
    
    stages {
        stage('DB Migration') {
            steps {
                withInfisical(configuration: [infisicalCredentialId: 'jenkins_universal_auth', infisicalEnvironmentSlug: 'dev', infisicalProjectSlug: 'k8s-ironcurtain-be', infisicalUrl: 'https://infisical.sabihinmolang.eu.org'], infisicalSecrets: [infisicalSecret(includeImports: true, path: '/', secretValues: [[infisicalKey: 'DATABASE_URL']])]) {
                    sh '''
                        # 1. Create a fresh virtual environment in the workspace
                        python3 -m venv .venv
                        
                        # 2. Install your dependencies (including prisma)
                        ./.venv/bin/pip install -r requirements.txt
                        
                        # 3. Execute the Prisma migration deployment
                        ./.venv/bin/python -m prisma migrate deploy
                    '''
                }
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
        stage('Tag to Quay') {
            steps {
                withInfisical(configuration: [infisicalCredentialId: 'jenkins_universal_auth', infisicalEnvironmentSlug: 'dev', infisicalProjectSlug: 'global-quay', infisicalUrl: 'https://infisical.sabihinmolang.eu.org'], infisicalSecrets: [infisicalSecret(includeImports: true, path: '/', secretValues: [[infisicalKey: 'QUAY_PASSWORD'], [infisicalKey: 'QUAY_HOSTNAME'], [infisicalKey: 'QUAY_USERNAME']])]) {
                    sh '''
                        docker tag ${APP_NAME}:latest ${QUAY_HOSTNAME}/${QUAY_USERNAME}/${APP_NAME}:latest
                    '''
                }
            }
        }
        stage('Push to Quay') {
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
