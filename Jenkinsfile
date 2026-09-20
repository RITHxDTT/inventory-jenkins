pipeline {
    agent any

    environment {
        DB_NAME = 'inventory_db'
        DB_HOST = 'host.docker.internal'
        DB_PORT = '5432'

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
                withCredentials([
                    usernamePassword(
                        credentialsId: 'inventory-postgres',
                        usernameVariable: 'DB_USER',
                        passwordVariable: 'DB_PASSWORD'
                    ),
                    string(
                        credentialsId: 'django-secret-key',
                        variable: 'SECRET_KEY'
                    )
                ]) {
                    sh '''
                        . .venv/bin/activate

                        python manage.py migrate --noinput
                    '''
                }
            }
        }

        stage('Collect Static') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'inventory-postgres',
                        usernameVariable: 'DB_USER',
                        passwordVariable: 'DB_PASSWORD'
                    ),
                    string(
                        credentialsId: 'django-secret-key',
                        variable: 'SECRET_KEY'
                    )
                ]) {
                    sh '''
                        . .venv/bin/activate

                        python manage.py collectstatic --noinput
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'inventory-postgres',
                        usernameVariable: 'DB_USER',
                        passwordVariable: 'DB_PASSWORD'
                    ),
                    string(
                        credentialsId: 'django-secret-key',
                        variable: 'SECRET_KEY'
                    )
                ]) {
                    sh '''
                        . .venv/bin/activate

                        python manage.py check
                        pytest
                    '''
                }
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