pipeline {
    agent any
    stages {
        stage('Build') {
            steps {                
                echo "Building..."
                sh "bash -c 'uname -a && cat /etc/issue'"    
                sh "bash -c 'sudo docker run --rm -v /var/run:/var/run -v $PWD:/code docker build --target ci -t python-ci /code -f /code/ci/Dockerfile'"                                            
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