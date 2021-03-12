import cmd2
from database import UseDB as db
from tabulate import tabulate
import re


def check_args(args):
    # TODO: Парсить аргументы без разделителей
    # parsed_args =
    args_dict = dict(zip(['name', 'ip', 'type', 'msg'],
                         args))

    print(args_dict)

    if len(args_dict) < 3:
        return 1
    elif "msg" not in args_dict:
        args_dict["msg"] = f'{args_dict["name"]} on {args_dict["ip"]} is not avaible'
    elif args_dict['type'] not in ['ups', 'ap', 'pc', '1', '2', '3']:
        return 2

    return args_dict


class Cli(cmd2.Cmd):
    def do_disable(self, args):
        # TODO: Добавить возможность отключать диапазоны ус-в
        '''Отключить устройство, синтаксис: disable <номер_ус-ва>'''
        print("disable")

    def do_delete(self, args):
        '''Удалить устройство по id, узнать можно из list'''
        print(args.split())
        resp = db().remove_device(args.split()[-1])
        print("Успешно!")

    def do_add(self, args):
        '''Добавляет устройство в список, синтаксис:
add <Название> <ip> <тип> <Сообщение (опционально)>'''
        print(args)
        args_dict = check_args(args.split())
        if type(args_dict) is int:
            print({1: "Недостаточно аргументов",
                   2: "Тип указан неправильно (0/ups, 1/ap - AP/Net, 2/pc - PC)"
                   }[args_dict])
        else:
            print(args_dict)
            db().add_device(args_dict["name"],
                            args_dict["ip"],
                            args_dict["type"],
                            args_dict["msg"])

            print("Успешно добавлено")

    def do_list(self, args):
        '''Выводит список добавленных устройств устройств'''
        raw_data = db().get_all()
        data2be_printed = []
        for row in raw_data:
            dev_type = {0: 'UPS',
                        1: 'AP/Switch',
                        2: 'PC'}[int(row[3])]
            if dev_type != 'AP/Switch':
                dev_status = {0: 'Dead',
                              1: 'Alive',
                              2: 'Disabled'}[int(row[5])]
            else:
                dev_status = 'Alive' if int(row[5]) > 0 else 'Dead'

            data2be_printed.append([row[0],
                                    row[1],
                                    row[2],
                                    dev_type,
                                    row[4],
                                    dev_status])

        table_headers = ['id', 'Name', 'IP', 'Type', 'Message', 'Status']
        print(tabulate(data2be_printed, headers=table_headers))

    def default(self, line):
        print("Неверная команда")

    def __init__(self):
        cmd2.Cmd.__init__(self)
        self.prompt = "> "
        self.intro = "Monitoringus CLI, напишите 'help' для справки"
        self.doc_header = "Доступные команды (для справки по конкретной командe наберите 'help <команда>')"


if __name__ == "__main__":
    cli = Cli()
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("Завершение сеанса")
