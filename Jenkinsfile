pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                
                echo "Building.."
                sh('ls -la')
                sh('pwd')
                sh('docker run -it --rm hello-world')
                sh('''#!/bin/bash
                ./jenkins.sh
                ./main.sh --builder
                ''')            
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