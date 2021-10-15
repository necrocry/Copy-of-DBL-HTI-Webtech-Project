pipeline {
    agent any
    environment {
        CONTAINER_NAME = "vis-project"
    }
    stages {
      
        stage('Build') {
            steps {
                //  Building new image
                sh 'docker image build -t $CONTAINER_NAME:latest .'
         //       sh 'docker image tag $DOCKER_HUB_REPO:latest $DOCKER_HUB_REPO:$BUILD_NUMBER'

                //  Pushing Image to Repository
         //       sh 'docker push desynchd/docker101tutorial:$BUILD_NUMBER'
           //     sh 'docker push desynchd/docker101tutorial:latest'
                
                echo "Image built and pushed to repository"
            }
        }
        stage('Deploy') {
            steps {
                script{
                    //sh 'BUILD_NUMBER = ${BUILD_NUMBER}'
                    if (BUILD_NUMBER == "1") {
                        sh 'docker run --name $CONTAINER_NAME -d -p 5000:5000'
                    }
                    else {
                        sh 'docker stop $CONTAINER_NAME'
                        sh 'docker rm $CONTAINER_NAME'
                        sh 'docker run --name $CONTAINER_NAME -d -p 5000:5000'
                    }
                    sh 'echo "Latest image/code deployed"'
                }
            }
        }
    }
}
