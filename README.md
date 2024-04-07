
<div align="center">
<p>
<img src="http://img.shields.io/static/v1?label=STATUS&message=EM%20DESENVOLVIMENTO&color=red" #whisper-server/>
<img alt="Version metadata URL badge" src="https://img.shields.io/badge/docker-v1.0.0--beta-blue">
<img alt="platform badge" src="https://img.shields.io/badge/whisper-20231117-aquamarine">
<img alt="Python Version Support (specify version) badge" src="https://img.shields.io/badge/Python-3.8.13-yellow">
<img alt="PyTorch Version Support (specify version) badge" src="https://img.shields.io/badge/PyTorch-1.13-blueviolet">
<img  alt="License"  src="https://img.shields.io/badge/license-MIT-brightgreen">
</p>

  <img width="200" src="https://git.ibict.br/cgti/whisper-server/-/wikis/uploads/126afea66c32e2bc62ed7e690f815183/Whisper2B.png">

<h1 align="center">Whisper Server</h1>

</div>

Whisper Server é um servidor robusto projetado para facilitar a transcrição de áudio usando o modelo Whisper da OpenAI. Este servidor é especialmente útil para aplicações que requerem conversão precisa de fala em texto, oferecendo suporte tanto para processamento sequencial quanto paralelo de arquivos de áudio. A implementação é facilmente acessível por meio de uma imagem Docker pré-configurada e pode ser utilizada em uma variedade de contextos, desde análises de dados até desenvolvimento de assistentes virtuais.

## Características

- **Processamento Sequencial e Paralelo**: Suporte para processamento de um arquivo de áudio por vez (`queue-transcribe`) ou vários arquivos simultaneamente (`parallel-transcribe`).
- **Flexibilidade de Modelos**: Diversas opções de modelos, desde `tiny` até `large-v3`, adequados para diferentes necessidades de qualidade e desempenho.
- **Compatibilidade de Dispositivos**: Funciona tanto em CPUs quanto em GPUs (CUDA), permitindo flexibilidade dependendo do hardware disponível.

## Instalação

O Whisper Server está disponível como uma imagem Docker, facilitando a instalação e a execução em qualquer ambiente compatível:
```bash
docker pull git.ibict.br:5050/cgti/whisper-server
```

## Iniciando o Container

Para iniciar o container e configurar o ambiente adequadamente, incluindo volumes para modelos e arquivos de áudio, execute:

```bash
docker run --name whisper --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 --gpus all -v ${PWD}/models:/root/.cache/whisper -v ${PWD}/audio-files:/app/audio-files -p 5000:5000 git.ibict.br:5050/cgti/whisper-server
```

- `--name whisper`: Atribui o nome whisper ao container, facilitando sua identificação e gerenciamento.

- `--ipc=host`: Define o namespace IPC (Inter-Process Communication) do container como sendo o mesmo do host. Isso é útil para alguns casos de uso específicos que exigem comunicação entre processos dentro do container e o host.

- `--ulimit memlock=-1`: Remove os limites de bloqueio de memória, permitindo que o container aloque mais memória de forma eficiente. O valor -1 significa sem limites.

- `--ulimit stack=67108864`: Define o limite máximo de tamanho da pilha (stack) para os processos dentro do container. O valor 67108864 corresponde a 64MB, que é geralmente suficiente para a maioria das aplicações.

- `--gpus all`: Permite que o container acesse todas as GPUs disponíveis no sistema host. Isso é crucial para tarefas de computação intensiva, como a transcrição de áudio feita pelo Whisper.

- `-v ${PWD}/models:/root/.cache/whisper`: Monta um volume que mapeia o diretório models no diretório de trabalho atual (${PWD}) para /root/.cache/whisper dentro do container. Isso é utilizado para armazenar e acessar os modelos do Whisper, evitando a necessidade de baixá-los repetidamente.

- `-v ${PWD}/audio-files:/app/audio-files`: Semelhante ao volume anterior, este mapeia o diretório audio-files do host para /app/audio-files no container. Isso permite o acesso aos arquivos de áudio que serão processados.

- `-p 5000:5000`: Mapeia a porta 5000 do container para a porta 5000 do host, permitindo o acesso aos endpoints do servidor Whisper pela rede do host.

- `git.ibict.br:5050/cgti/whisper-server`: Especifica a imagem do Docker a ser usada para criar o container. Esta imagem contém todos os arquivos e configurações necessárias para executar o servidor Whisper.

## Acesso ao Container para Testes e Monitoramento
Para acessar o container, execute o comando Docker exec com o ID do seu container:
```bash
docker exec -it <container_id> /bin/bash
```

Dentro do container, você pode realizar testes de transcrição:
```bash
whisper /app/audio-files/file.mp3 --device cpu --model base --language Portuguese --output_dir /app --output_format txt
```
```bash
whisper /app/audio-files/file.mp3 --device cuda --model large-v3 --language Portuguese --output_dir /app --output_format txt
```

Dentro do container, você pode monitorar o uso da GPU:
```bash
watch -n 1 nvidia-smi
```

Substitua <container_id> pelo ID do seu container. Você pode encontrar o ID do container executando docker ps.


## Uso

Após a instalação, o servidor pode ser iniciado na porta 5000. Existem dois endpoints principais disponíveis para transcrição de áudio:

- **Transcrição Sequencial (`queue-transcribe`)**: Processa um arquivo de áudio por vez.
- **Transcrição Paralela (`parallel-transcribe`)**: Capaz de processar vários arquivos de áudio simultaneamente.

### Endpoints

| Endpoint                 | Descrição                               |
|--------------------------|-----------------------------------------|
| `/queue-transcribe`      | Para processamento sequencial de áudio. |
| `/parallel-transcribe`   | Para processamento paralelo de áudio.   |

### Parâmetros dos Endpoints

Ambos os endpoints aceitam os seguintes parâmetros via POST:

- **audio**: O arquivo de áudio a ser processado.
- **model**: O modelo de transcrição desejado. Opções incluem: `tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3`.
- **device**: Especifica o dispositivo de processamento (`cpu` ou `cuda`).

## Modelos Disponíveis

| Tamanho  | Parâmetros | Inglês-Only | Multilíngue |
|----------|------------|-------------|-------------|
| tiny     | 39 M       | ✓           | ✓           |
| base     | 74 M       | ✓           | ✓           |
| small    | 244 M      | ✓           | ✓           |
| medium   | 769 M      | ✓           | ✓           |
| large    | 1550 M     | x           | ✓           |
| large-v2 | 1550 M     | x           | ✓           |
| large-v3 | 1550 M     | x           | ✓           |

## Exemplo de Requisição

Para realizar uma transcrição, você pode usar uma ferramenta como `curl`. Aqui está um exemplo de como enviar uma requisição para o endpoint `queue-transcribe`:

```bash
curl -X POST -F "audio=@/path/to/your/audio/file.wav" -F "model=base" -F "device=cuda" http://127.0.0.1:5000/queue-transcribe
```
**Substitua **: `/path/to/your/audio/file.wav` pelo caminho do seu arquivo de áudio, `model` pelo modelo desejado, e `device` pelo dispositivo de processamento.

## 🦸 Autor

  

<a  href="https://www.linkedin.com/in/deivdy-william-silva/">

<img  style="border-radius: 50%;"  src="https://avatars.githubusercontent.com/u/32515147?v=4"  width="100px;"  alt=""/>

<br  />

<sub><b>Deivdy William Silva</b></sub></a>  <a  href="http://lattes.cnpq.br/7257211063411329"  title="Lattes">👨‍🔬</a>

<br  />

  

[![Twitter Badge](https://img.shields.io/badge/-@Deivdy7William-1ca0f1?style=flat-square&labelColor=1ca0f1&logo=twitter&logoColor=white&link=https://twitter.com/Deivdy7William)](https://twitter.com/Deivdy7William) [![Linkedin Badge](https://img.shields.io/badge/-Deivdy-blue?style=flat-square&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/deivdy-william-silva/)](https://www.linkedin.com/in/deivdy-william-silva/)

[![Gmail Badge](https://img.shields.io/badge/-deivdy.william@gmail.com-c14438?style=flat-square&logo=Gmail&logoColor=white&link=mailto:deivdy.william@gmail.com)](mailto:deivdy.william@gmail.com)

  …
## 📝 Licença

  

Este projeto esta sobe a licença [MIT](./LICENSE).

  

Feito por Deivdy William Silva 👋🏽 [Entre em contato!](https://www.linkedin.com/in/deivdy-william-silva/)

  

---

  

## Versões do README

  

[Português 🇧🇷](./README.md)

