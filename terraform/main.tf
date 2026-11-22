terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_dynamodb_table" "zipcode" {
  name         = "ZipCode"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "ZipCode"
  range_key    = "PlaceName"

  attribute {
    name = "ZipCode"
    type = "S"
  }
  attribute {
    name = "PlaceName"
    type = "S"
  }
}

resource "aws_dynamodb_table" "reading" {
  name         = "Reading"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "Zip_DateTime"
  range_key    = "DateTime"

  attribute {
    name = "Zip_DateTime"
    type = "S"
  }
  attribute {
    name = "DateTime"
    type = "S"
  }
}

resource "aws_dynamodb_table" "error" {
  name         = "Error"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UUID"
  range_key    = "Zip_DateTime"

  attribute {
    name = "UUID"
    type = "S"
  }
  attribute {
    name = "Zip_DateTime"
    type = "S"
  }
}