library(rjson)
all_concepts = fromJSON(file = '/Users/zhouzhenyu/personal_repos/TextbookExtraction/all_word_info_StatisticalModels.json')
concepts_names = sapply(all_concepts, function(x) x$concept)

get_words = function(word_name){
  idx = which(concepts_names == word_name)
  pages = all_concepts[[idx]]$info$page
  res = data.frame(word_name = rep(word_name,length(pages)),pages = pages)
  return(res)
}
pre =c('distribution function','chi-squared distribution','markov process','directed acyclic graph',
       'contingency table')
post = c('survivor function','pearson’s statistic','gibbs sampler','moral graph',
         'analysis of variance')
test_pairs = data.frame(pre,post)
library(dplyr)
library(ggplot2)
library(ggridges)
library(ggthemes)
pair = unlist(test_pairs[3,])

analysis_pair = function(pre,post){
  pre_df = get_words(pre)
  post_df = get_words(post)
  df = rbind(pre_df,post_df)
  ggplot(df,aes(x=pages))+geom_bar(aes(fill = factor(word_name)))
  
  ggplot(df,aes(x=pages))+geom_histogram(aes(fill = factor(word_name)))
  
  plot = df %>%
    ggplot(aes(y=factor(word_name),x=pages,fill=word_name)) +
    geom_density_ridges()+
    scale_y_discrete(name='concept')+
    scale_fill_excel_new()+
    theme(axis.title.x = element_text(face="bold", colour="#990000", size=12),
                                axis.text.x  = element_text(angle=90, vjust=0.5,hjust=0.3, size=12),
                                axis.text.y = element_text(size=12,angle=30,vjust =-0.5),
                                axis.title.y = element_text(face="bold", colour="#990000", size=12))
  print(plot)
  
  res = df %>% 
    group_by(word_name) %>%
    count()
  return(res)
}
analysis_pair(test_pairs[1,1],test_pairs[1,2])
analysis_pair(test_pairs[2,1],test_pairs[2,2])
analysis_pair(test_pairs[3,1],test_pairs[3,2])
analysis_pair(test_pairs[4,1],test_pairs[4,2])
analysis_pair(test_pairs[5,1],test_pairs[5,2])
analysis_pair(concepts_names[3329],concepts_names[683])

analysis_pair('central limit theorem','mean')
