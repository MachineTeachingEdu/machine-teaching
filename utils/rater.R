install.packages("irr")
library(irr)

data <- read.csv('rater_masked.csv', header=FALSE)
# the "C" data from Krippendorff
nmm<-matrix(c(1,1,NA,1,2,2,3,2,3,3,3,3,3,3,3,3,2,2,2,2,1,2,3,4,4,4,4,4,
              1,1,2,1,2,2,2,2,NA,5,5,5,NA,NA,1,1,NA,NA,NA,NA, NA, NA ,NA),nrow=4)
# first assume the default nominal classification
kripp.alpha(nmm)
# now use the same data with the other three methods
kripp.alpha(nmm,"ordinal")
kripp.alpha(nmm,"interval")
kripp.alpha(nmm,"ratio") 
