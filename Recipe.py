class Recipe:
    def __init__(self):
        self.__steps = []
        self.__ingredients = []
        self.__current_step = 0
        self.__step_progress = 0

    def get_current_step(self):
        return self.__current_step

    def get_step_progress(self):
        return self.__step_progress

    def set_steps(self, steps):
        self.__steps = steps

    def set_ingredients(self, ingredients):
        self.__ingredients = ingredients

    def set_current_step(self, current_step):
        self.__current_step = current_step

    def set_step_progress(self, step_progress):
        self.__step_progress = step_progress

    def read_whole_recipe(self):
        whole_recipe = ""
        return whole_recipe.join(self.__steps)

    def read_current_step(self):
        step_string = self.__steps[self.__current_step]
        self.set_current_step(self.__current_step + 1)
        return step_string

    def read_given_step(self, index): # give index from handler
        return self.__steps[index]

    def move_to_given_step(self, index): # give index from handler
        step_string = self.__steps[index]
        self.set_current_step(index + 1)
        return step_string

    def read_all_ingredients(self):
        all_ingredients = ""
        return all_ingredients.join(self.__ingredients)

    def confirm_ingredient(self):
        repeat_ingredient_sentences = []
        sentences = self.__steps[self.__current_step].split('.')
        for sentence in sentences:
            ingredient_sentence = False
            words = sentence.split(" ")
            for word in words:
                if self.__ingredients.__contains__(word):
                    ingredient_sentence = True
            if ingredient_sentence:
                repeat_ingredient_sentences.append(sentence)
        all_ingredient_sentences = ""
        return all_ingredient_sentences.join(repeat_ingredient_sentences)

    def process_step_progress(self):
        num = 0
        number = False
        sentences = self.__steps[self.__current_step].split('.')
        for sentence in sentences:
            words = sentence.split(" ")
            for word in words:
                if number and word.contains("minute", "hour", "second"):
                    number = False
                    self.__step_progress -= num
                    break
                try:
                    num = int(word)
                    number = True
                except ValueError:
                    continue
        return str(self.get_step_progress())

# TODO: how to implement dynamic step_progress?
