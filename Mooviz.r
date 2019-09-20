library(shiny)
library(shinydashboard)
library(shinyjs)
library(shinyWidgets)
library(dashboardthemes)
# librairies d'import de données
library(RMySQL)
# librairies de manipulation des données
library(dplyr)



connected<-reactiveValues(a=2)

#Liste d'utilsateurs (Nom de compte puis mot de passe (chacun dans l'ordre associé))
user_n<-list("gn","admin","l")
user_p<-list("gnp","adminp","lp")


#On retire le header
head(NULL,n=5)
header <- dashboardHeader(disable=TRUE) 

ui <- dashboardPage(
    
  header,

  dashboardSidebar(collapsed = TRUE,
                   
                   valueBox( "Maf","CradMovieTech", icon = icon("atlas"),width=12,color="red"),
                   
                   uiOutput("Titre"),
                   uiOutput("Producteur"),
                   uiOutput("Directeur"),
                  
                   chooseSliderSkin("Nice",color="#7043c3"),
                   setSliderColor("red",1),
                   uiOutput("Dates")
  ),
  
  dashboardBody(
    shinyDashboardThemes(
      theme = "grey_dark"
    ),

    #Activation de shinyJs pour cacher/activer des éléments selon un condition ( de login pour nous )
    shinyjs::useShinyjs(),

    
    #Fenetre texte pour entrée les ID de login
    textInput('username', 'username', placeholder = 'admin'),
    passwordInput('password', 'password', placeholder = 'adminp'),
    
    #Bouton de login/logout
    actionButton('login', 'Login'),
    actionButton('logout', 'Logout'),
    
    # Affichage de la table correspondant a la selection
    dataTableOutput("table")
  ))

server <- function(input, output, session) {

  # Observe si la connection a été effectué 
  observe({
    connected$a
    
    #Utilisation de shinyjs pour afficher ou cacher des éléments selon l'etat de connection
    if (connected$a==1) {
      
      shinyjs::removeClass(selector = "body", class = "sidebar-collapse")
      shinyjs::show("table")
      
      shinyjs::show("logout")
      shinyjs::hide("login")
      
      shinyjs::hide("username")
      shinyjs::hide("password")
     
    }
    else {
     
      shinyjs::addClass(selector = "body", class = "sidebar-collapse")
      shinyjs::hide("table")
      
      shinyjs::hide("logout")
      shinyjs::show("login")
      
      shinyjs::show("username")
      shinyjs::show("password")
    }
  })
  
  #Systeme de login
  observeEvent(input$login, {
    
    #Si les deux entrée correspondent à des strings contenuent dans leur liste respective on passe à la suite
    if (input$username%in%user_n & input$password%in%user_p) {
      g=1
      #Boucle qui va vérifier que l'identifiant est bien associé au mdp
      for (i in user_n){
        if (user_n[g]==input$username && user_p[g]==input$password){
          #Si c'est le cas on met l'id session dans le cookie
          connected$a=1
          
          break
        }
        else {
          connected$a=2
        }
        g=g+1
        print(connected)
      }
    } 
  })
  
  #Si on appuie sur logout, nous deconnecte 
  observeEvent(input$logout, {
    connected$a=2
  })
  
   table_origine <- reactive({
    
     opt_bdd="BDD_Maxime"
     mydb <- dbConnect(MySQL(), default.file='/home/maxime/Téléchargements/.datalab.cnf', group='myBDD', dbname=opt_bdd)
     df<-dbReadTable(mydb,"`FILMS`")
     df2<-dbReadTable(mydb,"`CASTS`")
     dbDisconnect(mydb)
     
     df

  })
   
  
  table_selection <- reactive({
    
    #Filtre en fonction des recherches effectué
     if (is.null(input$Producteur) & is.null(input$Titre) & is.null(input$FR_nom))
     {
       table_origine() %>%
         dplyr::filter(Film_Ann >= input$Dates[1] & Film_Ann <= input$Dates[2])
     }
    
    else if (is.null(input$Producteur) & is.null(input$Titre)){
      table_origine() %>%
        dplyr::filter(Film_Ann >= input$Dates[1] & Film_Ann <= input$Dates[2],
                      FR_nom %in% input$FR_nom)
    }
    else if (is.null(input$Producteur) & is.null(input$FR_nom)){
      table_origine() %>%
        dplyr::filter(Film_Ann >= input$Dates[1] & Film_Ann <= input$Dates[2],
                      Film_Nom %in% input$Titre)
    }
    else if (is.null(input$Titre) & is.null(input$FR_nom)){
      table_origine() %>%
        dplyr::filter(Film_Ann >= input$Dates[1] & Film_Ann <= input$Dates[2],
                      FP_nom %in% input$Producteur)
    }
    
    else if (is.null(input$Titre)){
      table_origine() %>%
        dplyr::filter(Film_Ann >= input$Dates[1] & Film_Ann <= input$Dates[2],
                      FP_nom %in% input$Producteur,
                      FR_nom %in% input$FR_nom)
    }
    else if (is.null(input$Producteur)){
      table_origine() %>%
        dplyr::filter(Film_Ann >= input$Dates[1] & Film_Ann <= input$Dates[2],
                      Film_Nom %in% input$Titre,
                      FR_nom %in% input$FR_nom)
    }
    else if (is.null(input$FR_nom)){
      table_origine() %>%
        dplyr::filter(Film_Ann >= input$Dates[1] & Film_Ann <= input$Dates[2],
                      FP_nom %in% input$Producteur,
                      Film_Nom %in% input$Titre)
    }
    
    else{
       table_origine() %>%
         dplyr::filter(Film_Ann >= input$Dates[1] & Film_Ann <= input$Dates[2],
                       FP_nom %in% input$Producteur,
                       Film_Nom %in% input$Titre,
                       FR_nom %in% input$FR_nom)
    }
      
  })
  

  output$table <- renderDataTable(
    table_selection(),
    options = list(
      paging=TRUE,
      pageLength = 20,
      columnDefs = list(list(width = '200px', targets = "_all"))),
    
    
  )
    
    output$Producteur <- renderUI({
    liste_Producteur <- unique(table_origine()$FP_nom)
    selectizeInput('Producteur', 'Producteur', choices = liste_Producteur,multiple=TRUE)
    })
  
  output$Titre <- renderUI({
    liste_Titre <- unique(table_origine()$Film_Nom)
    selectizeInput('Titre', 'Titre', choices = liste_Titre,multiple=TRUE)
  })
  
  output$Directeur <- renderUI({
    liste_FR_nom <- unique(table_origine()$FR_nom)
    selectizeInput('FR_nom', 'Directeur', choices = liste_FR_nom,multiple=TRUE)
  })
  
  output$Dates <- renderUI({
  sliderInput("Dates",
              "Dates de sortie :",
              min = 1881,
              max =  max(table_origine()$Film_Ann),
              value = c(min(1881), max(table_origine()$Film_Ann)))
  
})
}

shinyApp(ui = ui, server = server)