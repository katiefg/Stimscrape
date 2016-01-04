rm(list=ls())

#Install necessary packages
list.of.packages <- c("topicmodels","RTextTools","DescTools")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only = TRUE)

#user-specified parameters
maxTopics <- 30 #maximum number of topics to explore
numTopics <- 10 #number of topics to extract for final run
critical_term <- "heroin" #make this heroin
topNterms <- 50
limitcorpus <- 1000 #limit of number of corpus entries - necessary for memory reasons

#load corpus
setwd('C:/Users/CHATHC01/Documents/D3Project/Spivack/Tasks/Stimscrape')
data <- read.csv('opiates_comments_11-16-15_more.csv')

#data cleaning - remove deleted, empty, and get rid of last (word or wordfragment) so that we don't have wordfragments clipped by our 255 character limitation on stemming
data <- as.character(data$comments)
data <- data[data != 'deleted '] #removed deleted comments
data <- data[data != ''] #removed empty comments
data <- data[sample(1:NROW(data),size=limitcorpus,replace=FALSE)]
data <- substr(data,1,255) #limit to first 255 characters for limitatio in stemming
strReverse <- function(x) #define and use reverse function to get last space
  sapply(lapply(strsplit(x, NULL), rev), paste, collapse="")
data_rev <- strReverse(data)
data_last_space <- StrPos(data_rev," ") #this is the position of the last space
data_last_space[is.na(data_last_space)] <- 0 #anything without a space is set to zero
data_nchar <- nchar(data) #for formatting reasons make sure it's all chars
data <- StrLeft(data,data_nchar-data_last_space) #get everything up until the last space, so we don't end up with half-words

#create the matrix for the CTM
matrix <- NULL
matrix <- create_matrix(data, language="english", removeNumbers=TRUE, stemWords=TRUE, weighting=tm::weightTf)

#remove empty rows
rowTotals <- apply(matrix , 1, sum) #Find the sum of words in each row
empty.rows <- matrix[rowTotals == 0, ]$dimnames[1][[1]]
data <- data[-as.numeric(empty.rows)]

#recreate document term matrix
matrix <- NULL
matrix <- create_matrix(data, language="english", removeNumbers=TRUE, stemWords=TRUE, weighting=tm::weightTf)

#Run CTM 
logliks <- NULL
for (k in 2:maxTopics){
  ctm <- NULL
  ctm <- CTM(matrix, k = k)
  logliks$k[k] <- k
  logliks$LL[k] <- sum(ctm@loglikelihood)
  print(paste('NumTopics: ',k,' LogLik: ',logliks$LL[k],sep=""))
  plot(logliks$k,logliks$LL)
  }

ctm <- CTM(matrix, k = numTopics)
lda <- LDA(matrix, k = numTopics)

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
