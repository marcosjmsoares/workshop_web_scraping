class BrowserML:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--start-maximized")
        # Adicione outras opções conforme necessário
        self.driver = webdriver.Chrome(options=self.chrome_options)
