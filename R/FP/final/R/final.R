#' NBA Players's profile.
#'
#' @param wiki A series of websites.
#' @return the data obtained, the summary of dat and a rds file of data \code{info}
#' @examples
#' Not a function and it is weird to make it a function I think, so, no example
library(xml2)
library(rvest)
library(httr)
library(purrr)
library(stringr)
library(dplyr)
library(tidyr)
NBA <- read_html("https://en.wikipedia.org/wiki/List_of_foreign_NBA_players")
nba <- html_node(x=NBA, xpath='//*[@id="mw-content-text"]/div/table[3]')
a=html_table(nba)
b=as.data.frame(a[1:50,1:6])
for (i in 1:50){
  if (b[i, 2]=='—') b[i, 2]=b[i, 1]
}


n=str_extract(b$Player, ".*\\,\\s[A-Z][^[A-Z]]*")
lastn=str_extract(n, ".*\\,") %>% str_replace("\\,", "")
firstn=str_extract(n, "\\s.*") %>% str_replace("\\s", "")
link=paste(firstn, lastn, sep = "_") %>% str_replace("J. _Bremer", "J._R._Bremer")%>% str_replace("Juan _Sánchez", "Juan_Ignacio_Sánchez")%>% str_replace("Rafael_Araújo", "Rafael_Araújo_(basketball)")
linklist=map_chr(link, ~ paste("https://en.wikipedia.org/wiki", ., sep="/"))
linklist[1:5]


get_wiki_info <- function(url){
  wiki <- read_html(url)
  info <- html_node(x=wiki, ".vcard")
  table=html_table(info, header=FALSE, fill = TRUE)
  colnames(table) <- c("key", "value")
  d=data.frame(table[,1:2])
  r=filter(d, key=="Born"|key== "Listed height"|key== "Listed weight"|key== "High school"|key== "College"|key== "NBA draft")
  hrow=c("High school", "NA")
  crow=c("College", "NA")
  drow=c("NBA draft", "NA")
  if (!("High school" %in% r$key)) r=rbind(r, hrow)
  if (!("College" %in% r$key)) r=rbind(r, crow)
  if (!("NBA draft" %in% r$key)) r=rbind(r, drow)
  rr=spread(r, key = key, value = value)
  return(rr)
}

result=data.frame(Born=character(0), Listed_height=character(0), Listed_weight=character(0), High_school=character(0), College=character(0), NBA_draft=character(0))
for (i in 1:50) {
  if (linklist[i]!="https://en.wikipedia.org/wiki/Ian_Lockhart") {
    m=get_wiki_info(linklist[i])
    result=rbind(result, m)
  }
  else {
    empty=c("NA", "NA", "NA", "NA")
    result=rbind(result, empty)
  }
}
result


info=cbind(b, result)
info$Born = info$Born %>% str_replace("\u00A0", " ") %>% str_replace("\u00F1", "")
info$`Listed height` = info$`Listed height`  %>% str_replace_all("\u00A0", " ")
info$`Listed weight` = info$`Listed weight` %>% str_replace_all("\u00A0", " ")
saveRDS(info, "wikidata.rds")
info


table(year=info$Yrs)
weight=info$`Listed weight` %>% str_extract("\\d+\\slb") %>% str_replace(" lb", "")
weight=map_dbl(weight, ~ as.numeric(.))
summary(weight)
height=info$`Listed height` %>% str_extract(".*m") %>% str_extract(".{5}m")
table(height)

