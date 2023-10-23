# from HUGGINGFACE - https://huggingface.co/blog/blip-2
#
# from PIL import Image
# import requests
# from transformers import Blip2Processor, Blip2ForConditionalGeneration
# import torch
#
# device = "cuda" if torch.cuda.is_available() else "cpu"
#
#
# def generate_text_from_image(url):
#     processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
#     model = Blip2ForConditionalGeneration.from_pretrained(
#         "Salesforce/blip2-opt-2.7b", torch_dtype=torch.float16
#     )
#     model.to(device)
#     image = Image.open(requests.get(url, stream=True).raw)
#     inputs = processor(images=image, return_tensors="pt").to(device, torch.float16)
#     generated_ids = model.generate(**inputs)
#     generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[
#         0].strip()
#     return generated_text
#
#
# print(generate_text_from_image())
