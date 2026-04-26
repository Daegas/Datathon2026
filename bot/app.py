from pathlib import Path

from shiny import App, ui, render, reactive
from predictor import responder_mensaje

app_ui = ui.page_fluid(
    ui.include_css(Path(__file__).with_name("styles.css")),
    ui.div(
        ui.h2("Chatbot"),
        ui.output_ui("chat"),
        ui.layout_columns(
            ui.input_text("user_msg", "Mensaje", placeholder="Escribe un user_id (ej. USR-00003)"),
            ui.input_action_button("send", "Enviar", class_="btn-primary"),
            col_widths=(10, 2),
        ),
        class_="chat-wrapper",
    ),
)

def server(input, output, session):
    # Estado del chat por sesión para evitar compartir mensajes entre usuarios.
    messages = reactive.Value([])

    @reactive.effect
    @reactive.event(input.send)
    def _():
        msg = input.user_msg().strip()
        if not msg:
            return

        chat = list(messages.get())
        bot_reply = responder_mensaje(msg)
        
        chat.append(("Usuario", msg))
        chat.append(("Bot", bot_reply))
        messages.set(chat)
        ui.update_text("user_msg", value="")

    @output
    @render.ui
    def chat():
        history = messages.get()
        if not history:
            return ui.div(
                ui.p("Todavía no hay mensajes. Escribe algo para comenzar.", class_="chat-empty"),
                class_="chat-history",
            )

        bubbles = []
        for speaker, text in history:
            bubble_class = "msg msg-user" if speaker == "Usuario" else "msg msg-bot"
            bubbles.append(ui.div(text, class_=bubble_class))

        return ui.div(*bubbles, class_="chat-history")

app = App(app_ui, server)