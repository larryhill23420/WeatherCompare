package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
@RestController
public class DemoApplication {

    private final RestTemplate restTemplate = new RestTemplate();
    private static final String COMPARE_URL = "https://ocw3et6rrpypcwcoeaj7gqzliy0oksgx.lambda-url.us-west-2.on.aws/";

    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }

    @GetMapping("/compare")
    public String compare(
            @RequestParam String zip1,
            @RequestParam String zip2,
            @RequestParam(defaultValue = "1") int days) {

        String url = COMPARE_URL + "?zip1=" + zip1 + "&zip2=" + zip2 + "&days=" + days;
        return restTemplate.getForObject(url, String.class);
    }
}