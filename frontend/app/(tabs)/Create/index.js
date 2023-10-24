import * as React from "react";
import { useState, useEffect, useRef, useContext } from "react";
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  Button,
  ScrollView,
  Image,
  SafeAreaView,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import Slider from "@react-native-community/slider";
import LottieView from "lottie-react-native";
import CustomButton from "../../../components/customButton";
import * as Speech from "expo-speech";
import Constants from "expo-constants";
import { UserContext } from "../_layout";

const uri = Constants?.expoConfig?.hostUri
  ? Constants.expoConfig.hostUri.split(`:`).shift().concat(`:8080`)
  : `/create`;

renderWithData = async (
  t,
  min,
  setGenText,
  setDriveName,
  setUser,
  demo = false
) => {
  console.log("----");
  if (demo) {
    // New
    console.log("IN DEMO");
    setUser(
      "https://drive.google.com/uc?export=view&id=" +
        "1TtWk3uo0jTC0BR2CAlaH8DgcRtp0hDCb"
    );
    return;

    console.log("demo");
    await Audio.setAudioModeAsync({
      staysActiveInBackground: true,
      interruptionModeAndroid: 1,
      shouldDuckAndroid: false,
      playThroughEarpieceAndroid: false,
      allowsRecordingIOS: false,
      interruptionModeIOS: 1,
      playsInSilentModeIOS: true,
    });
    const { sound } = await Audio.Sound.createAsync(require("./demo.mp3"));
    setSound(sound);
    setDriveName("demo");
    setGenText("demo demo demo");
    console.log("yada");
    return;
  }

  console.log("----");
  fetch_url = "http://" + uri + `/create?topic=${t}&min=${min}`;
  console.log(fetch_url);
  const response = await fetch(fetch_url);
  const res = await response.json();
  console.log(res);
  console.log("-----create");
  // För att få ljuduppselning in the background men verkar bara funka i standalone app
  // const { sound } = await Audio.Sound.createAsync({
  //   uri: "https://drive.google.com/uc?export=view&id=" + res["name"],
  // });
  setUser("https://drive.google.com/uc?export=view&id=" + res["name"]) //"https://drive.google.com/uc?export=view&id=" + res["name"])
  // setSound(sound);
  // setDriveName(res["name"]);
  // setGenText(res["text"]);
  // console.log("-------Done");
};

export default function index() {
  const animation = useRef(null);
  const [topic, setTopic] = useState("");
  const [length, setLength] = useState(1);
  const [genText, setGenText] = useState("");
  const [driveName, setDriveName] = useState("");
  const { user, setUser } = useContext(UserContext);

  // React.useEffect(() => {
  //   console.log("-- in mount ---");
  //   async function setAudioMode() {
  //     await Audio.setAudioModeAsync({
  //       allowsRecordingIOS: false,
  //       staysActiveInBackground: true,
  //       interruptionModeIOS: InterruptionModeIOS.DuckOthers,
  //       playsInSilentModeIOS: true,
  //       shouldDuckAndroid: true,
  //       interruptionModeAndroid: InterruptionModeAndroid.DuckOthers,
  //       playThroughEarpieceAndroid: false,
  //     });
  //   }
  //   setAudioMode();
  // }, []);

  return (
    <ScrollView style={styles.scrollView} keyboardShouldPersistTaps="handled">
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
              renderWithData(
                topic,
                length,
                setGenText,
                setDriveName,
                setUser,
                false
              );
            }}
            title="Create"
          />
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
    paddingBottom: 300,
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
