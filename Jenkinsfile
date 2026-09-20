pipeline {
    agent any

    environment {
        DB_NAME = 'inventory_db'
        DB_HOST = 'host.docker.internal'
        DB_PORT = '5432'

        // Jenkins Credentials
        DB_CREDS = credentials('inventory-postgres')
        SECRET_KEY = credentials('django-secret-key')

        // Docker
        DOCKER_IMAGE = 'idkisme/inventory'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Setup') {
            steps {
                sh '''
                    python3 --version

                    python3 -m venv .venv
                    . .venv/bin/activate

                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Database Migration') {
            steps {
                sh '''
                    . .venv/bin/activate

                    export DB_USER=$DB_CREDS_USR
                    export DB_PASSWORD=$DB_CREDS_PSW

                    python manage.py migrate --noinput
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . .venv/bin/activate

                    export DB_USER=$DB_CREDS_USR
                    export DB_PASSWORD=$DB_CREDS_PSW

                    python manage.py check
                    pytest
                '''
            }
        }

        stage('Package') {
            steps {
                sh '''
                    docker build \
                      -t ${DOCKER_IMAGE}:${IMAGE_TAG} \
                      -t ${DOCKER_IMAGE}:latest .
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully."
            echo "Docker image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
        }

        failure {
            echo "Pipeline failed."
        }
    }
}