pipeline {
    agent {
        kubernetes {
        yaml '''
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              - name: docker
                image: docker:latest
                command:
                - cat
                tty: true
                volumeMounts:
                - mountPath: /var/run/docker.sock
                  name: docker-sock
              volumes:
              - name: docker-sock
                hostPath:
                path: /var/run/docker.sock    
            '''
        }
  }
    stages {
        stage('Clone') {
            steps {
                container('docker') {
                    echo "Cloning.."
                    sh "git clone https://github.com/orenzah/k8s-stock-trading"    
                }            
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