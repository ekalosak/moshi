module Main exposing (main)

import Browser
import Html exposing (Html, div, text)
import Time

main =
  Browser.sandbox { init = 0, update = update, view = view }

type alias Model =
  { val : Int
  , updated : Bool
  }

type Msg = Some Int | None

update msg model =
  case msg of
    Some val ->
      val
    None ->
      -1

view model =
  div []
    [
      div [] [ text (String.fromInt model) ]
    ]
