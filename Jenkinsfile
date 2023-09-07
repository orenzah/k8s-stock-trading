pipeline {
    agent any
    stages {
        stage('Build') {
            steps {                
                echo "Building..."
                sh "bash -c 'uname -a && cat /etc/issue'"                
                sh "bash -c 'sudo docker run -it --rm hello-world'"
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
                sh "bash -c 'main.sh --deployer'"
            }
        }
    }
}