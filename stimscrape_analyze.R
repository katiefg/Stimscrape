#Install necessary pacakges
list.of.packages <- c("topicmodels","RTextTools")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only = TRUE)

#user-specified parameters
numTopics <- 3
critical_term <- "campaign" #make this heroin
topNterms <- 10

#load corpus
data("NYTimes", package = "RTextTools")
data <- NYTimes[sample(1:3100,size=1000,replace=FALSE),]

#create the matrix for the CTM
matrix <- create_matrix(data$Subject, language="english", removeNumbers=TRUE, stemWords=TRUE, weighting=weightTf)

#Run CTM with number of topics pre-specified
ctm <- CTM(matrix, k = numTopics)

#find top N terms for each topic
ctm_posterior <- posterior(ctm) 
topterms_by_topic <- NULL
for (topic in numTopics:1){ #go in reverse order so first column in topterms_by_topic will correspond to the first topic
  ctm_posterior_terms <- exp(ctm_posterior$terms[topic,])-1 #convert from log space
  topterms_by_topic$terms <- cbind(topterms_by_topic$terms,names(sort(ctm_posterior_terms, decreasing=TRUE)[1:topNterms]))
  topterms_by_topic$probs <- cbind(topterms_by_topic$probs,sort(ctm_posterior_terms, decreasing=TRUE)[1:topNterms])
}
rownames(topterms_by_topic$probs) <- NULL #nullify the misleading row names

#find heroin topic number
critical_term_topicno <- which(topterms_by_topic$terms==critical_term,arr.ind = TRUE)[,2]
