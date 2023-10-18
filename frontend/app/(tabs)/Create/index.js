import React, { useState, useEffect, useRef } from "react";
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  Button,
  ScrollView,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import Slider from "@react-native-community/slider";
import LottieView from "lottie-react-native";
import CustomButton from "../../../components/customButton";
import * as Speech from "expo-speech";
import Constants from "expo-constants";

const uri = Constants?.expoConfig?.hostUri
  ? Constants.expoConfig.hostUri.split(`:`).shift().concat(`:3000`)
  : `/create`;
renderWithData = async (t, min, setGenText) => {
  console.log("----")
  fetch_url = "http://" + uri + `/create?topic=${t}&min=${min}`
  console.log(fetch_url)
  const response = await fetch(fetch_url);
  console.log(response)
  const res = await response.json();
  console.log(res)
  setGenText(res);
};

export default function index() {
  const animation = useRef(null);
  const [topic, setTopic] = useState("");
  const [length, setLength] = useState(1);
  const [genText, setGenText] = useState("");
  return (
    <ScrollView style={styles.scrollView} keyboardShouldPersistTaps='handled'>
      <View style={styles.container}>
        <View style={styles.top}>
          <StatusBar style="auto" />
          <LottieView
            autoPlay
            ref={animation}
            style={{
              width: 250,
              height: 250,
              backgroundColor: "#fff",
            }}
            source={require("../../../assets/pod.json")}
          />
          <Text style={{ marginTop: 25 }}>What do you want to listen to?</Text>
          <TextInput
            value={topic}
            onChangeText={(topic) => setTopic(topic)}
            placeholder={"The industrial revolution..."}
            style={styles.input}
          />
          <Text>How long do you want to listen?</Text>
        <Slider
          value={length}
          onValueChange={(value) => setLength(value)}
          style={{ width: 250, height: 40 }}
          minimumValue={1}
          maximumValue={5}
          step={1}
          minimumTrackTintColor="#000000"
          maximumTrackTintColor="#e8e8e8"
        />
        <Text style={{ left: ((length - 1) / 1) * 50 - 10 }}>
          {length} mintues
        </Text>
        </View>
        <View style={styles.bottom}>
          <CustomButton
            onPress={() => {
              renderWithData(topic, length, setGenText);
            }}
            title="Create"
          />
          {genText.length < 5 ? (
            <View></View>
          ) : (
            <View>
              <Button
                title="Press to Start"
                onPress={() =>
                  Speech.speak(genText, {
                    language: "en-US",
                    pitch: 1,
                    rate: 1,
                  })
                }
              />
              <Button title="pause" onPress={() => Speech.pause()} />
              <Button title="resume" onPress={() => Speech.resume()} />
            </View>
          )}
        </View>
        <Text>{genText}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollView: {
    backgroundColor: "#FFF",
  },
  container: {
    flex: 1,
    backgroundColor: "#fff",
    alignItems: "center",
    justifyContent: "center",
  },
  top: {
    flex: 3,
    alignItems: "left",
    justifyContent: "flex-end",
  },
  bottom: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  input: {
    width: 250,
    height: 44,
    padding: 10,
    marginTop: 5,
    marginBottom: 20,
    backgroundColor: "#e8e8e8",
  },
});
