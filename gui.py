import typing
from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import *

from acribis_scores import *

SCORES = {'CHA2DS2-VASc': (chads_vasc.Parameters, chads_vasc.calc_chads_vasc_score),
          'SMART': (smart.Parameters, smart.calc_smart_score),
          'MAGGIC': (maggic.Parameters, maggic.calc_maggic_score)}


class Calculator(Frame):
    def __init__(self, master: Misc | None = None, padding=10, **kwargs):
        super().__init__(master=master, padding=padding, **kwargs)
        self.winfo_toplevel().title('Calculator')
        self.grid()
        self.__form = None
        self.__fields = None
        self.__parameters = {}
        self.__selected_score = StringVar(self)
        self.__result = StringVar(self, 'Result: ---')
        self.__result_label = Label(self, textvariable=self.__result)
        self.__result_label.grid(column=1, row=2)
        Label(self, text='Selected Score:').grid(column=0, row=0)
        OptionMenu(self, self.__selected_score, next(iter(SCORES)), *SCORES.keys()).grid(column=1, row=0)
        Button(self, text='Calculate', command=self.calc_score).grid(column=1, row=3)
        self.__selected_score.trace('w', self.__update__)
        self.__build_form__()

    def __build_form__(self):
        self.__form = Frame(self)
        self.__form.grid()
        self.__form.grid(column=0, row=1, columnspan=2)
        self.__fields = typing.get_type_hints(SCORES[self.__selected_score.get()][0])
        i = 0
        for parameter, input_type in self.__fields.items():
            Label(self.__form, text=parameter).grid(column=0, row=i)
            if input_type is bool:
                var = BooleanVar(self, False)
                Checkbutton(self.__form, variable=var).grid(column=1, row=i)
            else:
                var = StringVar(self)
                reg = self.register(self.__validate_input__)
                parameter_escaped = parameter.replace('%', '%%')
                Entry(self.__form, textvariable=var, validate='key',
                      validatecommand=(reg, parameter_escaped, '%P')).grid(column=1, row=i)
            self.__parameters[parameter] = var
            i += 1

    def __validate_input__(self, parameter, value):
        if not value:
            return True
        try:
            self.__fields[parameter](value)
            return True
        except ValueError:
            self.bell()
            return False

    def __update__(self, *_):
        self.__form.destroy()
        self.__parameters.clear()
        self.__build_form__()
        self.__result.set('Result: ---')

    def calc_score(self):
        score_parameters = {}
        score = None
        for name, value in self.__parameters.items():
            if (type(value) is BooleanVar) or value.get():
                score_parameters[name] = self.__fields[name](value.get())
            else:
                showerror(title='Missing Values!', message=f"{name} is required but not provided as input!")
                return
        try:
            score = SCORES[self.__selected_score.get()][1](score_parameters)
        except ValueError as e:
            showerror(title='Values Error', message=str(e))
        self.__result.set(f"Result: {score}")
        print(score)


if __name__ == '__main__':
    root = Tk()
    Calculator(root)
    root.mainloop()
