class Recipe:
    def __init__(self, steps, ingredients, total_time):
        self.__steps = steps
        self.__ingredients = ingredients
        self.__current_step = 0
        self.__total_time = 0

    def get_current_step(self):
        return self.__current_step + 1

    def get_total_time(self):
        return self.__total_time

    def set_steps(self, steps):
        self.__steps = steps

    def set_ingredients(self, ingredients):
        self.__ingredients = ingredients

    def set_current_step(self, current_step):
        self.__current_step = current_step

    def set_total_time(self, total_time):
        self.__total_time = total_time

#     def read_whole_recipe(self):
#         whole_recipe = ""
#         return whole_recipe.join(self.__steps)

    def read_step(self):  # give index and increment current step from handler,
        step_sentence = self.__steps[self.__current_step]
        self.__current_step += 1
        return step_sentence

#     def move_to_given_step(self, index):  # give index and increment current step  from handler
#         step_string = self.__steps[index - 1]
#         self.set_current_step(index - 1)
#         return step_string

    def read_all_ingredients(self):
        all_ingredients = ""
        return all_ingredients.join(self.__ingredients)

    def confirm_ingredient(self):
        repeat_ingredient_sentences = []
        sentences = self.__steps[self.__current_step].split('.')
        for sentence in sentences:
            for ingredient in self.__ingredients:
                if ingredient in sentence:
                    repeat_ingredient_sentences.append(sentence)
                    break
        all_ingredient_sentences = ""
        return all_ingredient_sentences.join(repeat_ingredient_sentences)

#     def process_step_progress(self):
#         num = 0
#         number = False
#         sentences = self.__steps[self.__current_step].split('.')
#         for sentence in sentences:
#             words = sentence.split(" ")
#             for word in words:
#                 if number:
#                     number = False
#                     if "minute" in word:
#                         self.__step_progress -= num
#                     elif "second" in word:
#                         self.__step_progress -= num / 60.0
#                     elif "hour" in word:
#                         self.__step_progress -= num * 60
#                     break
#                 try:
#                     num = int(word)
#                     number = True
#                 except ValueError:
#                     continue
#         return str(self.get_step_progress())
