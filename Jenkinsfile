pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                containers:
                - name: maven
                    image: maven:alpine
                    command:
                    - cat
                    tty: true
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