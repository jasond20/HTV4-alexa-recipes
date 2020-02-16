import requests
import traceback
from lxml import html
import logging
import ask_sdk_core.utils as ask_utils
import os
from ask_sdk_s3.adapter import S3Adapter
s3_adapter = S3Adapter(bucket_name=os.environ["S3_PERSISTENCE_BUCKET"])

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello! Welcome to the cooking helper."
        reprompt_text = "What would you like to make?"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class InitializeRecipeIntentHandler(AbstractRequestHandler):
    """Handler for recipe initialization"""
    #returns ingredients and steps in a list
    def food_scraping(link):
        pageContent=requests.get(link)
        tree = html.fromstring(pageContent.content)

        i = 1
        ingredients = []
        ingredientsXpath = ['//*[@id="lst_ingredients_1"]/li[%i]/label/span/text()',
                            '//*[@id="lst_ingredients_2"]/li[%i]/label/span/text()']
        xPathCounter = 0
        ingredientsListNum = 1
        steps = []

        #read steps
        while(True):
            try:
                xPath = '//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ol/li[%x]/span/text()'%i
                i += 1
                step = tree.xpath(xPath)
                step = str(step)[2:len(str(step))-32]
                if len(step) == 0:
                    break
                steps.append(step)
                #print(step)
            except:
                #traceback.print_exc()
                break
        i = 1
        #ingredients list
        while(True):
            try:
                xPath = ingredientsXpath[xPathCounter]%i

                i += 1
                #print(xPath)
                ingredient = tree.xpath(xPath)
                ingredient =str(ingredient)[2:len(str(ingredient))-2]
                if ingredient == "Add all ingredients to the list":
                    break
                if len(ingredient) == 0:
                    xPathCounter+=1
                    i =1
                    if(xPathCounter>1):
                        break
                ingredients.append(ingredient)
                #print(ingredient)

            except:
                #traceback.print_exc()
                break

        prepTime = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[2]/time/span/span/text()')
        prepTime = str(prepTime)[2:len(str(prepTime))-2]
        #print(prepTime)

        prepTimeUnit = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[2]/time/span/text()')
        #print(prepTimeUnit)

        cookTime = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[3]/time/span/span/text()')
        #print(cookTime)

        cookTimeUnit = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[3]/time/span/text()')
        #print(cookTimeUnit)

        readyIn = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[4]/time/span/span/text()')
        #print(readyIn)

        readyInTimeUnit = tree.xpath('//*[@id="main-content"]/div[3]/section/section[2]/div/div[1]/ul/li[4]/time/span/text()')
        #print(readyInTimeUnit)

        return steps, ingredients
    #returns link and title of searched food
    def food_search(food):

        link = 'https://www.allrecipes.com/search/results/?wt=%s&sort=re'%food
        pageContent=requests.get(link)
        tree = html.fromstring(pageContent.content)

        optionlink = tree.xpath('//*[@id="fixedGridSection"]/article[2]/div[2]/h3//a/@href')
        optionlink = str(optionlink)[2:len(str(optionlink))-2]
        optionname = tree.xpath('//*[@id="fixedGridSection"]/article[2]/div[2]/h3/a/span/text()')

        #print(optionlink)
        return optionlink, optionname

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("InitializeRecipeIntent")(handler_input)
         
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        food = slots["Recipe"].value
        
    
        try:
            link, recipe_name = food_search(food)
            steps, ingredients_list = food_scraping(link)
            step_count = 0
        except:
            #print("no results")
            return (
            handler_input.response_builder
                .speak("I couldn't find any recipes.")
                .response
            )
        
        #recipe_name = ??? webscraper find recipe name
        #ingredients_list = ??? webscraper get ingredients list
        #steps_list = ??? webscraper get steps list <- add all of these to recipe_attributes
        #ingredient_count = 0
        #step_count = 0
        attributes_manager = handler_input.attributes_manager
        
        
        recipe_attributes = {
            "recipe_name": recipe_name,
            "steps" : steps,
            "ingredients_list" : ingredients_list,
            "step_count" : step_count
        }
        attributes_manager.persistent_attributes = recipe_attributes
        attributes_manager.save_persistent_attributes()
        
        
        speak_output = 'Here's a recipe for {recipe_name}.'.format(recipe_name=recipe_name)
        #^Here's a recipe for _
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask()
                .response
        )

class NextIngredientIntentHandler(AbstractRequestHandler):
    """Handler for stepping ingredients"""
    def can_handle(self, handler_input):
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("food" in attr)
        
        return ask_utils.is_intent_name("NextIngredientIntent")(handler_input) and attributes_are_present
         
    def handle(self, handler_input):
        speak_output = ""
        #^Replace with the stuff from processing/list of ingredients
        
        attr = handler_input.attributes_manager.persistent_attributes
        ingredient_count = attr['ingredient_count']
        
        if ingredient_count >= len(attr['ingredients_list']):
            return (
                handler_input.response_builder
                .speak("Done with ingredients. Try asking about the next step.")
                .ask()
                .response
            )
        
        attr["ingredient_count"] += 1
        speak_output = attr['ingredients_list'][ingredient_count]
        attributes_manager = handler_input.attributes_manager
        attributes_manager.persistent_attributes = attr
        attributes_manager.save_persistent_attributes()
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask()
                .response
        )

class NextStepIntentHandler(AbstractRequestHandler):
    """Handler for stepping steps"""
    def can_handle(self, handler_input):
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("food" in attr)
        
        return ask_utils.is_intent_name("NextStepIntent")(handler_input) and attributes_are_present
         
    def handle(self, handler_input):
        speak_output = ""
        #^Replace with the stuff from processing/list of steps
        
        attr = handler_input.attributes_manager.persistent_attributes
        step_count = attr['step_count']
        
        if step_count >= len(attr['steps']):
            return (
                handler_input.response_builder
                .speak("Finished all steps. You recipe is complete.")
                .ask()
                .response
            )
        attr["step_count"] += 1
        speak_output = attr['steps'][step_count]
        attributes_manager = handler_input.attributes_manager
        attributes_manager.persistent_attributes = attr
        attributes_manager.save_persistent_attributes()
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask()
                .response
        )

class PreviousStepIntentHandler(AbstractRequestHandler):
    """Handler for stepping steps"""
    def can_handle(self, handler_input):
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("food" in attr)
        
        return ask_utils.is_intent_name("PreviousStepIntent")(handler_input) and attributes_are_present
         
    def handle(self, handler_input):
        speak_output = ""
        #^Replace with the stuff from processing/list of steps
        
        attr = handler_input.attributes_manager.persistent_attributes
        step_count = attr['step_count']
        
        if step_count <= 0:
            return (
                handler_input.response_builder
                .speak("There is no previous step.")
                .ask()
                .response
            )
        attr["step_count"] -= 1
        speak_output = attr['steps'][step_count]
        attributes_manager = handler_input.attributes_manager
        attributes_manager.persistent_attributes = attr
        attributes_manager.save_persistent_attributes()
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask()
                .response
        )

class ConfirmationIntentHandler(AbstractRequestHandler):
    """Handler for step confirmation"""
    def can_handle(self, handler_input):
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("food" in attr)
        
        return ask_utils.is_intent_name("ConfirmationIntent")(handler_input) and attributes_are_present
         
    def handle(self, handler_input):
        speak_output = ""
        #^Replace with the stuff from processing/list of steps (Repeat current step)
        
        attr = handler_input.attributes_manager.persistent_attributes
        step_count = attr['step_count']
        speak_output = attr['steps'][step_count]
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask()
                .response
        )

class ConfirmIngredientIntentHandler(AbstractRequestHandler):
    """Handler for ingredient confirmation"""
    def can_handle(self, handler_input):
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("food" in attr)
        
        return ask_utils.is_intent_name("ConfirmIngredientIntent")(handler_input) and attributes_are_present
         
    def handle(self, handler_input):
        speak_output = ""
        #^Replace with the stuff from processing function/list of ingredients
        
        attr = handler_input.attributes_manager.persistent_attributes
        ingredient_count = attr['ingredient_count']
        speak_output = attr['ingredients_list'][ingredient_count]
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask()
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = ""

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(persistence_adapter=s3_adapter)

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(InitializeRecipeIntentHandler())
sb.add_request_handler(NextIngredientIntentHandler())
sb.add_request_handler(NextStepIntentHandler())
sb.add_request_handler(ConfirmationIntentHandler)
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
