import json, os, tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

class CharacterCreatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('RPG Character Creator - Ordem Paranormal')
        self.geometry('1050x600')
        self.resizable(True, True)

        self.char = {
            'name': '',
            'attributes': {},
            'skills': [],
            'characteristics': '',
            'image_path': ''
        }

        self.attributes_list = ['Agilidade', 'Intelecto', 'Vigor', 'Presença', 'Força']
        self.fixed_skills = [
            'Acrobacia+', 'Adestramento*', 'Artes*', 'Atletismo', 'Atualidades', 'Ciências*', 'Crime*',
            'Diplomacia', 'Enganação', 'Fortitude', 'Furtividade+', 'Intimidação', 'Investigação',
            'Luta', 'Medicina', 'Ocultismo*', 'Percepção', 'Pilotagem*', 'Pontaria', 'Reflexos',
            'Religião*', 'Sobrevivência', 'Tática*', 'Tecnologia*', 'Vontade'
        ]
        self.nex_var = tk.IntVar(value=5)

        self._build_ui()
        self.char['attr_image_path'] = 'https://crisordemparanormal.com/assets/attributes-V37qZCrP.png'

        if PIL_AVAILABLE:
            self.load_attr_image()

    def _build_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill='both', expand=True)

        left = ttk.Frame(main)
        right = ttk.Frame(main)
        left.pack(side='left', fill='both', expand=True)
        right.pack(side='right', fill='y')

        name_frame = ttk.Frame(left)
        name_frame.pack(fill='x', pady=2)
        ttk.Label(name_frame, text='Nome:').pack(side='left')
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var).pack(side='left', fill='x', expand=True, padx=6)

        notebook = ttk.Notebook(left)
        notebook.pack(fill='both', expand=True, pady=6)

        tab_attr = ttk.Frame(notebook)
        notebook.add(tab_attr, text='Atributos / Perícias')

        # Esquerda: atributos
        attr_left = ttk.Frame(tab_attr)
        attr_left.pack(side='left', fill='y', expand=False)

        attr_frame = ttk.LabelFrame(attr_left, text='Atributos')
        attr_frame.pack(fill='y', expand=False, padx=4, pady=4)

        self.attr_canvas = tk.Canvas(attr_frame, width=400, height=300, bg='gray80')
        self.attr_canvas.pack(fill='none', expand=False)
        self.attr_bg_image = None
        self.attr_spinboxes = {}
        self.attr_vars = {}

        self.attr_positions = {
            'Agilidade': (0.5, 0.19),
            'Intelecto': (0.75, 0.40),
            'Vigor': (0.67, 0.77),
            'Presença': (0.34, 0.77),
            'Força': (0.26, 0.41),
        }

        for a in self.attributes_list:
            var = tk.IntVar(value=1)
            self.attr_vars[a] = var

        bars_frame = ttk.Frame(attr_frame)
        bars_frame.pack(fill='x', expand=False, pady=(10, 0))

        # NEX
        nex_row = ttk.Frame(bars_frame)
        nex_row.pack(fill='x', pady=2)
        ttk.Label(nex_row, text='NEX%:').pack(side='left', padx=4)
        nex_spin = ttk.Spinbox(nex_row, from_=5, to=99, increment=5, textvariable=self.nex_var, width=5)
        nex_spin.pack(side='left')

        # Barras
        self.bars = {}
        bar_specs = [('Vida', 'red'), ('Sanidade', '#800080'), ('Esforço', 'orange')]
        for label, color in bar_specs:
            row = ttk.Frame(bars_frame)
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=label+':').pack(side='left', padx=4)
            max_var = tk.IntVar(value=10)
            cur_var = tk.IntVar(value=10)
            self.bars[label] = {'max': max_var, 'cur': cur_var}
            ttk.Entry(row, textvariable=max_var, width=4).pack(side='left')
            ttk.Label(row, text='<-Máx').pack(side='left', padx=2)
            ttk.Entry(row, textvariable=cur_var, width=4).pack(side='left')
            ttk.Label(row, text='<-Atual').pack(side='left', padx=2)
            bar_canvas = tk.Canvas(row, width=120, height=18, bg='white', highlightthickness=1, highlightbackground='#aaa')
            bar_canvas.pack(side='left', padx=8)
            def update_bar(canvas=bar_canvas, cur=cur_var, maxv=max_var, color=color):
                canvas.delete('all')
                try:
                    v = cur.get()
                    m = maxv.get()
                    if m <= 0: m = 1
                    frac = max(0, min(1, v/m))
                except Exception:
                    frac = 1
                canvas.create_rectangle(0, 0, 120, 18, fill='#eee', outline='')
                canvas.create_rectangle(0, 0, int(120*frac), 18, fill=color, outline='')
                canvas.create_text(60, 9, text=f'{v}/{m}', fill='black', font=('Arial', 9, 'bold'))
            max_var.trace_add('write', lambda *_, c=bar_canvas, cur=cur_var, maxv=max_var, col=color: update_bar(c, cur, maxv, col))
            cur_var.trace_add('write', lambda *_, c=bar_canvas, cur=cur_var, maxv=max_var, col=color: update_bar(c, cur, maxv, col))
            update_bar()

        # Perícias
        pericias_frame = ttk.LabelFrame(tab_attr, text='Perícias')
        pericias_frame.pack(side='left', fill='both', expand=True, pady=6, padx=6)

        pericias_canvas = tk.Canvas(pericias_frame)
        scrollbar = ttk.Scrollbar(pericias_frame, orient="vertical", command=pericias_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        pericias_canvas.pack(side="left", fill="both", expand=True)
        pericias_canvas.configure(yscrollcommand=scrollbar.set)

        self.pericias_container = ttk.Frame(pericias_canvas)
        self.pericias_container.bind("<Configure>", lambda e: pericias_canvas.configure(scrollregion=pericias_canvas.bbox("all")))
        pericias_canvas.create_window((0, 0), window=self.pericias_container, anchor="nw")

        # Cabeçalho
        header = ttk.Frame(self.pericias_container)
        header.pack(fill='x')
        ttk.Label(header, text='Nome').grid(row=0, column=0, padx=4)
        ttk.Label(header, text='Bônus').grid(row=0, column=1, padx=4)

        self.pericia_rows = []
        for skill in self.fixed_skills:
            self._add_pericia_row(name=skill, level=0)

        ttk.Label(self.pericias_container,
                text='+ Penalidade de carga. * Somente treinada.',
                foreground='gray').pack(anchor='w', pady=(4,0), padx=4)

        # Direita: coluna do personagem (imagem e ações) – agora expandida
        right = ttk.Frame(tab_attr)
        right.pack(side='left', fill='both', expand=True, padx=6, pady=6)

        img_frame = ttk.LabelFrame(right, text='Foto do Personagem')
        img_frame.pack(fill='x', pady=6)
        self.img_label = ttk.Label(img_frame, text='Nenhuma imagem')
        self.img_label.pack(padx=6, pady=6)
        ttk.Button(img_frame, text='Carregar Foto', command=self.load_image).pack(padx=6, pady=2)

        ttk.Button(right, text='Carregar imagem dos atributos', command=self.load_attr_image).pack(fill='x', pady=4)

        actions = ttk.LabelFrame(right, text='Ações')
        actions.pack(fill='x', pady=10)
        ttk.Button(actions, text='Salvar Personagem', command=self.save_character).pack(fill='x', pady=4)
        ttk.Button(actions, text='Carregar Personagem', command=self.load_character).pack(fill='x', pady=4)
        ttk.Button(actions, text='Limpar', command=self.clear_form).pack(fill='x', pady=4)

        if not PIL_AVAILABLE:
            msg = 'Recomendado instalar Pillow para suporte a imagens: pip install Pillow'
            ttk.Label(right, text=msg, foreground='red', wraplength=180).pack(padx=4, pady=6)

        # Tab 2: Habilidades / Rituais / Inventário
        tab_hab = ttk.Frame(notebook)
        notebook.add(tab_hab, text='Habilidades / Rituais / Inventário')

        hab_left = ttk.LabelFrame(tab_hab, text='Habilidades / Rituais')
        hab_left.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        self.hab_container = ttk.Frame(hab_left)
        self.hab_container.pack(fill='both', expand=True)
        header = ttk.Frame(self.hab_container)
        header.pack(fill='x')
        ttk.Label(header, text='Nome').grid(row=0, column=0, padx=4)
        ttk.Label(header, text='Nível').grid(row=0, column=1, padx=4)
        ttk.Button(header, text='Adicionar', command=self._add_habilidade_row).grid(row=0, column=2, padx=6)
        self.habilidade_rows = []

        inv_right = ttk.LabelFrame(tab_hab, text='Inventário')
        inv_right.pack(side='right', fill='both', expand=True, padx=4, pady=4)
        self.inv_container = ttk.Frame(inv_right)
        self.inv_container.pack(fill='both', expand=True)
        header = ttk.Frame(self.inv_container)
        header.pack(fill='x')
        ttk.Label(header, text='Item').grid(row=0, column=0, padx=4)
        ttk.Label(header, text='Peso').grid(row=0, column=1, padx=4)
        ttk.Button(header, text='Adicionar', command=self._add_inventario_row).grid(row=0, column=2, padx=6)
        self.inventario_rows = []

        # Tab 3: Descrições
        tab_desc = ttk.Frame(notebook)
        notebook.add(tab_desc, text='Descrições')
        desc_notebook = ttk.Notebook(tab_desc)
        desc_notebook.pack(fill='both', expand=True)

        self.desc_fields = {}
        sections = [('Notas', 'notes'), ('Aparência / Personalidade', 'appearance'), ('Histórico', 'history'), ('Objetivo', 'goal')]
        container = ttk.Frame(tab_desc)
        container.pack(fill='both', expand=True, padx=4, pady=4)
        for title, key in sections:
            lbl = ttk.Label(container, text=title)
            lbl.pack(anchor='w', pady=(6, 0))
            t = tk.Text(container, height=6)
            t.pack(fill='both', expand=False, padx=2, pady=2)
            self.desc_fields[key] = t

    def _add_skill_row(self, name='', level=0):
        return
    def _remove_skill_row(self, row_frame):
        return

    def load_attr_image(self):
        if not PIL_AVAILABLE:
            messagebox.showwarning('Pillow ausente', 'Instale Pillow para carregar imagens de atributos.')
            return
        url = 'https://crisordemparanormal.com/assets/attributes-V37qZCrP.png'
        try:
            from urllib.request import urlopen
            from io import BytesIO
            resp = urlopen(url, timeout=6)
            data = resp.read()
            img = Image.open(BytesIO(data))
            self._set_attr_canvas_image(img, source=url)
        except Exception as e:
            messagebox.showerror('Erro', f'Não foi possível carregar imagem online:\n{e}')

    def _set_attr_canvas_image(self, pil_image, source=''):
        w = self.attr_canvas.winfo_width() or 400
        h = self.attr_canvas.winfo_height() or 300
        img = pil_image.copy()
        img.thumbnail((w, h))
        self.attr_bg = ImageTk.PhotoImage(img)
        self.attr_canvas.delete('all')
        self.attr_bg_image = self.attr_canvas.create_image(w//2, h//2, image=self.attr_bg)
        self.char['attr_image_path'] = source
        self._place_attr_spinboxes(force_size=(400, 300))

    def _place_attr_spinboxes(self, force_size=None):
        for k, v in list(self.attr_spinboxes.items()):
            try:
                self.attr_canvas.delete(v['window_id'])
                v['widget'].destroy()
            except Exception:
                pass
        self.attr_spinboxes.clear()
        if force_size:
            width, height = force_size
        else:
            width = self.attr_canvas.winfo_width() or 400
            height = self.attr_canvas.winfo_height() or 300
        for name, (xp, yp) in self.attr_positions.items():
            x = int(xp * width)
            y = int(yp * height)
            var = self.attr_vars.get(name, tk.IntVar(value=1))
            sb = ttk.Spinbox(self.attr_canvas, from_=0, to=99, textvariable=var, width=4)
            window_id = self.attr_canvas.create_window(x, y, window=sb, anchor='center')
            self.attr_spinboxes[name] = {'widget': sb, 'window_id': window_id, 'var': var}
        self.attr_canvas.bind('<Configure>', lambda e: self._place_attr_spinboxes(force_size=(400, 300)))

    def _add_pericia_row(self, name='', level=0):
        row = ttk.Frame(self.pericias_container)
        row.pack(fill='x', pady=2, padx=4)
        ttk.Label(row, text=name).grid(row=0, column=0, sticky='w')
        level_var = tk.IntVar(value=level)
        spin = ttk.Spinbox(row, from_=0, to=15, increment=5, textvariable=level_var, width=5)
        spin.grid(row=0, column=1, padx=6)
        self.pericia_rows.append((row, name, level_var))

    def _remove_pericia_row(self, row_frame):
        for t in list(self.pericia_rows):
            if t[0] is row_frame:
                t[0].destroy()
                self.pericia_rows.remove(t)
                return

    def _add_habilidade_row(self, name='', level=0):
        row = ttk.Frame(self.hab_container)
        row.pack(fill='x', pady=2, padx=4)
        name_var = tk.StringVar(value=name)
        level_var = tk.IntVar(value=level)
        e_name = ttk.Entry(row, textvariable=name_var)
        e_name.grid(row=0, column=0, sticky='ew')
        e_level = ttk.Spinbox(row, from_=0, to=10, textvariable=level_var, width=5)
        e_level.grid(row=0, column=1, padx=6)
        btn = ttk.Button(row, text='Remover', command=lambda r=row: self._remove_habilidade_row(r))
        btn.grid(row=0, column=2, padx=6)
        row.columnconfigure(0, weight=1)
        self.habilidade_rows.append((row, name_var, level_var))

    def _remove_habilidade_row(self, row_frame):
        for t in list(self.habilidade_rows):
            if t[0] is row_frame:
                t[0].destroy()
                self.habilidade_rows.remove(t)
                return

    def _add_inventario_row(self, item='', peso=1):
        row = ttk.Frame(self.inv_container)
        row.pack(fill='x', pady=2, padx=4)
        item_var = tk.StringVar(value=item)
        peso_var = tk.IntVar(value=peso)
        e_item = ttk.Entry(row, textvariable=item_var)
        e_item.grid(row=0, column=0, sticky='ew')
        e_peso = ttk.Spinbox(row, from_=0, to=999, textvariable=peso_var, width=6)
        e_peso.grid(row=0, column=1, padx=6)
        btn = ttk.Button(row, text='Remover', command=lambda r=row: self._remove_inventario_row(r))
        btn.grid(row=0, column=2, padx=6)
        row.columnconfigure(0, weight=1)
        self.inventario_rows.append((row, item_var, peso_var))

    def _remove_inventario_row(self, row_frame):
        for t in list(self.inventario_rows):
            if t[0] is row_frame:
                t[0].destroy()
                self.inventario_rows.remove(t)
                return

    def load_image(self):
        path = filedialog.askopenfilename(title='Escolha uma foto', filetypes=[('Images', '*.png;*.jpg;*.jpeg;*.gif;*.bmp')])
        if not path:
            return
        if not PIL_AVAILABLE:
            messagebox.showwarning('Pillow ausente', 'Instale Pillow para carregar imagens corretamente.')
            self.img_label.config(text=os.path.basename(path))
            self.char['image_path'] = path
            return
        try:
            img = Image.open(path)
            img.thumbnail((250, 250))
            self.photo = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.photo, text='')
            self.char['image_path'] = path
        except Exception as e:
            messagebox.showerror('Erro', f'Não foi possível abrir a imagem:\n{e}')

    def _gather_data(self):
        data = {}
        data['name'] = self.name_var.get()
        data['attributes'] = {k: v.get() for k, v in self.attr_vars.items()}
        data['nex'] = self.nex_var.get()
        data['pericias'] = [
            {'name': name, 'bonus': var.get()}
            for _, name, var in self.pericia_rows if var.get() > 0
        ]
        data['habilidades'] = [{'name': s[1].get(), 'level': s[2].get()} for s in self.habilidade_rows if s[1].get().strip()]
        data['inventario'] = [{'item': s[1].get(), 'peso': s[2].get()} for s in self.inventario_rows if s[1].get().strip()]
        data['descriptions'] = {k: t.get('1.0', 'end').strip() for k, t in self.desc_fields.items()}
        data['attr_image_path'] = self.char.get('attr_image_path', '')
        data['image_path'] = self.char.get('image_path', '')
        data['barras'] = {}
        for nome, bar in self.bars.items():
            data['barras'][nome] = {
                'max': bar['max'].get(),
                'cur': bar['cur'].get()
            }
        return data

    def save_character(self):
        data = self._gather_data()
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')], title='Salvar personagem')
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo('Salvo', f'Personagem salvo em:\n{path}')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao salvar:\n{e}')

    def load_character(self):
        path = filedialog.askopenfilename(title='Carregar personagem', filetypes=[('JSON', '*.json')])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao ler arquivo:\n{e}')
            return
        self.name_var.set(data.get('name', ''))
        for k, v in data.get('attributes', {}).items():
            if k in self.attr_vars:
                try:
                    self.attr_vars[k].set(int(v))
                except Exception:
                    self.attr_vars[k].set(v)
        for row, _, _ in list(self.pericia_rows):
            row.destroy()
        self.pericia_rows.clear()
        for s in data.get('pericias', []):
            # Usa 'bonus' se existir; senão, mantém 0
            self._add_pericia_row(name=s.get('name', ''), level=s.get('bonus', 0))
        # Habilidades
        for row, _, _ in list(self.habilidade_rows):
            row.destroy()
        self.habilidade_rows.clear()
        for s in data.get('habilidades', []):
            self._add_habilidade_row(name=s.get('name', ''), level=s.get('level', 0))
        # Inventario
        for row, _, _ in list(self.inventario_rows):
            row.destroy()
        self.inventario_rows.clear()
        for it in data.get('inventario', []):
            self._add_inventario_row(item=it.get('item', ''), peso=it.get('peso', 1))
        # Restaurar barras
        barras = data.get('barras', {})
        for nome, bar in self.bars.items():
            vals = barras.get(nome, {})
            if 'max' in vals:
                try:
                    bar['max'].set(int(vals['max']))
                except Exception:
                    pass
            if 'cur' in vals:
                try:
                    bar['cur'].set(int(vals['cur']))
                except Exception:
                    pass
        imgp = data.get('image_path', '')
        if imgp:
            self.char['image_path'] = imgp
            if PIL_AVAILABLE and os.path.exists(imgp):
                try:
                    img = Image.open(imgp)
                    img.thumbnail((250, 250))
                    self.photo = ImageTk.PhotoImage(img)
                    self.img_label.config(image=self.photo, text='')
                except Exception:
                    self.img_label.config(text=os.path.basename(imgp), image='')
            else:
                self.img_label.config(text=os.path.basename(imgp), image='')
        # Imagem de atributos
        attr_imgp = data.get('attr_image_path', '')
        if attr_imgp:
            if PIL_AVAILABLE:
                try:
                    if os.path.exists(attr_imgp):
                        img = Image.open(attr_imgp)
                        self._set_attr_canvas_image(img, source=attr_imgp)
                    else:
                        from urllib.request import urlopen
                        from io import BytesIO
                        resp = urlopen(attr_imgp, timeout=6)
                        img = Image.open(BytesIO(resp.read()))
                        self._set_attr_canvas_image(img, source=attr_imgp)
                except Exception:
                    pass
        self.nex_var.set(data.get('nex', 5))

    def clear_form(self):
        self.name_var.set('')
        for v in self.attr_vars.values():
            v.set(1)
        for r, _, _ in list(self.pericia_rows):
            r.destroy()
        self.pericia_rows.clear()
        for r, _, _ in list(self.habilidade_rows):
            r.destroy()
        self.habilidade_rows.clear()
        for r, _, _ in list(self.inventario_rows):
            r.destroy()
        self.inventario_rows.clear()
        for t in self.desc_fields.values():
            t.delete('1.0', 'end')
        for bar in self.bars.values():
            bar['max'].set(10)
            bar['cur'].set(10)
        self.img_label.config(image='', text='Nenhuma imagem')
        self.char['image_path'] = ''

if __name__ == '__main__':
    app = CharacterCreatorApp()
    app.mainloop()
