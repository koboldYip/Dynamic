import matplotlib.pyplot as plt

capacity = 18000  # Емкость максимальная
initCharge = 10000  # Стартовый заряд в 0-ой час
# Цена за кВтч
priceSchedule = [1.5, 1.5, 1.5, 1.5,
                 1.5, 1.5, 2, 3, 5,
                 5, 5, 4.5, 3, 3, 3,
                 3, 4.5, 5, 7, 9,
                 11, 12, 8, 4]
# Переменная нагрузка
loadSchedule = [480, 320, 320, 360, 360,
                360, 420, 920, 1200, 720,
                680, 720, 800, 820, 960,
                1200, 1380, 1380, 1520,
                1800, 1920, 1920, 1640,
                1020]
constantLoad = 320  # Постоянная нагрузка
targetCharge = 7000  # Минимальное ограничение заряда в конце дня
#  Шаг торговых операций
chargeValue = [-4000, -3000, -2000, -1000, 0, 1000, 2000, 3000, 4000]


# Основная операция расчета поиска оптимального решения
def forward_calculating(dictionary):
    index_of_best_value = 0
    counter = 9  # Количество торговых операций, в начале 9 штук, как и шагов торговых операций
    best_value = float('-inf')
    # Цикл по часам, начинаем со второго часа и идем до 24-ого
    # Исходный словарь с вычисленными значениями первого часа
    for k in range(2, 25):
        # Счетчик обнуляем, имеющийся счетчик заносим в iteration_value, по которому и идет следующий цикл
        # Он 9 только в начале, если тебе кажется зачем это здесь
        # Дальше он из нуля увеличивается только когда мы заходим по ветвлению в саму операцию вычисления
        iteration_value, counter = counter, 0
        for i in range(iteration_value):
            # Ну логично что внутри вычисления мы выполняемая все возможные торговые операции
            for j in chargeValue:
                try:  # Эту классную штуку ниже обсудим
                    # Собственно само ветвление которое увеличивает счетчик,
                    # То есть вычисление запускается только когда торговая операция не вытолкнет нас за ограничения
                    # Емкость меньше 0 или больше максимального заряда
                    # Соответственно и счетчик будет нести в себе число оставшихся операций
                    # Ибо зачем если у нас при оставшихся условно 7 ебашить все 9, ну типа лол
                    if (0 <= (dictionary['g' + str(k - 1) + str(i)] -
                              (loadSchedule[k - 1] + constantLoad) + j) <= capacity):

                        # Тут считаем целевую функцию, оно же выгода, прибыл деньги, шекели
                        dictionary['f' + str(k) + str(counter)] = \
                            (dictionary['f' + str(k - 1) + str(i)]) + \
                            (priceSchedule[k - 1] * (j * -0.001))

                        # Тут у нас считается оставшийся заряд батареи
                        dictionary['g' + str(k) + str(counter)] = \
                            (dictionary['g' + str(k - 1) + str(i)] -
                             (loadSchedule[k - 1] + constantLoad) + j)

                        # Тут торговая операция этого вычисления
                        # В принципе можно как то сделать по другому
                        # Но я её здесь сохранял чтобы по ней воссоздавать путь назад из лучшего решения
                        dictionary['x' + str(k) + str(counter)] = j
                        # Ну тут итог для 24-го часа
                        if k == 24:
                            # Если конечный заряд меньше минимального сразу такое удаляем
                            if dictionary['g' + str(k) + str(counter)] < targetCharge:
                                removing_objectionable(counter, dictionary, k)
                            # А вот если заряд равен или больше требуемого
                            # А само значение целевой функции, выгода, бабло, шекели лучше, чем то что мы уже нашли
                            # То это у нас новое лучшее решение
                            elif ((dictionary['g' + str(k) + str(counter)] >= targetCharge) & (
                                    dictionary[
                                        'f' + str(k) + str(counter)] > best_value)):
                                best_value = dictionary['f' + str(k) + str(counter)]
                                index_of_best_value = counter
                        # Ну и собственно инкриментируем счетчик, что это прекрасное вычисление нам подходит
                        # и можно будет его обрабатывать дальше
                        counter += 1
                # Классная штука которую мы обсуждали в try, она помогает обходить ключи которых в это словаре нет
                # Обходить именно ошибку их отсутствия, а не то что ты обрабатываешь значение которого нет
                except KeyError:
                    continue
        # Здесь удаляем похожие строки, ну тип, в одно значение можно прийти разными путями, и как бы вроде бы заряд
        # Одинаковый, но выгода разная, так что смотрим где мы пришли в похожий заряд,
        # а вот оставляем только лучший по выгоде вариант без этой штуки кстати комп заебется считать
        # потому что ну лол я бы сам нахуй послал если бы сказали считать такое, это уже реально тупой перебор,
        # даже если учесть то что мы отбрасываем варианты вылета за границы
        # так что previous здесь это не предыдущий час, а именно значение в одном столбце,
        # надеюсь ты понимаешь о чем я...
        for m in range(counter):
            for l in range(counter):
                try:
                    this_capacity = dictionary['g' + str(k) + str(m)]
                    previous_capacity = dictionary['g' + str(k) + str(l)]
                    this_function_value = dictionary['f' + str(k) + str(m)]
                    previous_function_value = dictionary['f' + str(k) + str(l)]
                    if (this_capacity == previous_capacity) & \
                            (this_function_value >= previous_function_value) & \
                            (m != l):
                        removing_objectionable(l, dictionary, k)
                except KeyError:
                    continue
    return dictionary, index_of_best_value, best_value


# Удаление чтобы несколько раз не писать одинаковую помойку
def removing_objectionable(counter, dictionary, k):
    del dictionary['x' + str(k) + str(counter)]
    del dictionary['g' + str(k) + str(counter)]
    del dictionary['f' + str(k) + str(counter)]


# Здесь мы уже из лучшего значения восстанавливаем маршрут назад,
# здесь то и нужен этот х, а в целом я думаю понятно что здесь происходит,
# просто восстанавливаем мощность по сохраненным операциям с нагрузкой
def reverse_folding(dict_calc_final, best_value_index):
    final_mass = [k for k in range(24)]
    num_of_best_function = best_value_index
    final_mass[0] = initCharge
    final_mass[23] = dict_calc_final['g' + str(24) + str(best_value_index)]
    dict_calc_len = len(dict_calc_final)
    for k in range(22):
        previous_value = dict_calc_final['g' + str(24 - k) + str(num_of_best_function)] - \
                         dict_calc_final['x' + str(24 - k) + str(num_of_best_function)] + \
                         (loadSchedule[24 - k - 1] + constantLoad)
        for i in range(dict_calc_len):
            try:
                if dict_calc_final['g' + str(24 - k - 1) + str(i)] == previous_value:
                    final_mass[24 - k - 2] = previous_value
                    num_of_best_function = i
            except KeyError:
                continue
    return final_mass


table = {}

# Тут создаем табличку со значениями первого часа
for i in range(len(chargeValue)):
    table['x' + str(i)] = chargeValue[i]
    table['f1' + str(i)] = priceSchedule[0] * (chargeValue[i] * -0.001)
    table['g1' + str(i)] = initCharge - (loadSchedule[0] + constantLoad) + chargeValue[i]

# Эту табличку первого часа запускаем в вычисление
dict_24, index_of_best_value, best_value = forward_calculating(table)

print("Значение наилучшей целевой функции: ", best_value)

# Здесь восстанавливаем маршрут оптимальный
final_mass = reverse_folding(dict_24, index_of_best_value)

print("Значения заряда батареи для оптимальных торговых операций: ")
print(final_mass)

without_sale_charge = []

# Вычисление поведения без торговых операций
for i in range(24):
    initCharge -= (constantLoad + loadSchedule[i])
    without_sale_charge.append(initCharge)

# Графики
time = [i for i in range(24)]
plt.plot(time, without_sale_charge, label="Без торгов")
plt.plot(time, final_mass, label="С учетом торгов")

plt.grid()
plt.xlabel('Время (час)')
plt.ylabel('Уровень заряда (Втч)')
plt.legend()

plt.show()
