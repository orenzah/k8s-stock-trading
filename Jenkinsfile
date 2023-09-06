pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo "Building.."
                bash -c "main.sh --builder --base"
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
                bash -c "main.sh --deployer"
            }
        }
    }
}