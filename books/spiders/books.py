from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

class Articulo(Item):
    titulo = Field()
    precio = Field()
    descripcion = Field()
    ventas = Field()
    #fabricante = Field()
    #marca = Field()
    #nombre = Field()
    preguntas = Field()

class MercadoLibreCrawler(CrawlSpider):
    name = 'mercadoLibre'

    custom_settings = {
      'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36',
      #'CLOSESPIDER_PAGECOUNT': 100 # Numero maximo de paginas en las cuales voy a descargar items. Scrapy se cierra cuando alcanza este numero
    }

    # Utilizamos 2 dominios permitidos, ya que los articulos utilizan un dominio diferente
    #allowed_domains = ['articulo.mercadolibre.com.ec', 'listado.mercadolibre.com.ec']
    allowed_domains = ['listado.mercadolibre.com.pe', 'articulo.mercadolibre.com.pe']
    #allowed_domains = ['listado.mercadolibre.com.pe', 'articulo.mercadolibre.com.pe']
    #start_urls = ['https://listado.mercadolibre.com.ec/animales-mascotas/perros/']
    #start_urls = ['https://listado.mercadolibre.com.pe/chocolates']
    #start_urls = ['https://listado.mercadolibre.com.pe/otras-categorias/alimentos-bebidas/']
    start_urls = ['https://listado.mercadolibre.com.pe/otras-categorias/alimentos-bebidas/chocolates#D[A:chocolates,on]']


    download_delay = 2

    # Tupla de reglas
    rules = (
        Rule( # REGLA #1 => HORIZONTALIDAD POR PAGINACION
            LinkExtractor(
                #allow=r'/chocolates_Desde_\d+' # Patron en donde se utiliza "\d+", expresion que puede tomar el valor de cualquier combinacion de numeros
                allow=[r'/chocolates',r'/chocolates_Desde_51',r'/chocolates_Desde_101', r'/chocolates_Desde_151',r'/chocolates_Desde_201']

            ), follow=True),
        Rule( # REGLA #2 => VERTICALIDAD AL DETALLE DE LOS PRODUCTOS
            LinkExtractor(
                allow=r'/MPE-'
            ), follow=True, callback='parse_items'), # Al entrar al detalle de los productos, se llama al callback con la respuesta al requerimiento
    )

    def parse_items(self, response):

        item = ItemLoader(Articulo(), response)
        
        # Utilizo Map Compose con funciones anonimas
        # PARA INVESTIGAR: Que son las funciones anonimas en Python?
        item.add_xpath('titulo', '//h1/text()', MapCompose(lambda i: i.replace('\n', ' ').replace('\r', ' ').strip()))
        #item.add_xpath('fabricante', '//div[@class="ui-pdp-specs__table"]//tr[1]/td')
        #item.add_xpath('marca', '//div[@class="ui-pdp-specs__table"]//tr[2]/td')
        #item.add_xpath('nombre', '//div[@class="ui-pdp-specs__table"]//tr[3]/td')
        item.add_xpath('descripcion', '//div[@class="ui-pdp-description"]/p/text()', MapCompose(lambda i: i.replace('\n', ' ').replace('\r', ' ').strip()))
        item.add_xpath('ventas','//ul[@class="ui-pdp-seller__list-description"]/li[3]/strong/text()')
        item.add_xpath('precio','//span[@class="price-tag-fraction"]/text()')
        item.add_xpath('preguntas', '//span[@class="ui-pdp-color--BLACK ui-pdp-size--SMALL ui-pdp-family--REGULAR ui-pdp-questions__questions-list__question"]/text()')
        #soup = BeautifulSoup(response.body)
        #precio = soup.find(class_="price-tag")
        #precio_completo = precio.text.replace('\n', ' ').replace('\r', ' ').replace(' ', '') # texto de todos los hijos
        #item.add_value('precio', precio_completo)

        yield item.load_item()
