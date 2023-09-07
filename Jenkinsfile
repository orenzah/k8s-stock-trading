pipeline {
  agent {
    kubernetes {
      label 'dind'            
    }
  }
  stages {    
    stage('Run Docker Things') {
        agent {

        }
      steps {
        container('dind') {
          sh 'docker ps'
        }
      }
    }
  }
}