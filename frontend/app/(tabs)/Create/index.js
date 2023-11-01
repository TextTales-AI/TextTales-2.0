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
  Pressable,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import Slider from "@react-native-community/slider";
import LottieView from "lottie-react-native";
import CustomButton from "../../../components/customButton";
import * as Speech from "expo-speech";
import Constants from "expo-constants";
import { UserContext } from "../_layout";
import { Picker } from "@react-native-picker/picker";

const uri = Constants?.expoConfig?.hostUri
  ? Constants.expoConfig.hostUri.split(`:`).shift().concat(`:3000`)
  : `/create`;

renderWithData = async (t, min, style, voice, setGenText, setDriveName, setUser) => {
  console.log("----");
  fetch_url = "http://" + uri + `/create?topic=${t}&min=${min}&style=${style}&voice=${voice}`;
  console.log(fetch_url);
  const response = await fetch(fetch_url);
  const res = await response.json();
  console.log(res);
  console.log("-----create");
  // För att få ljuduppselning in the background men verkar bara funka i standalone app
  // const { sound } = await Audio.Sound.createAsync({
  //   uri: "https://drive.google.com/uc?export=view&id=" + res["name"],
  // });
  setUser("https://drive.google.com/uc?export=view&id=" + res["name"]); //"https://drive.google.com/uc?export=view&id=" + res["name"])
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
  const [category, setCategory] = useState("NEWS");
  const { user, setUser } = useContext(UserContext);
  const [selectedVoice, setSelectedVoice] = useState("Bella");

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
  const news_color = category == "NEWS" ? "black" : "#c9c9c9";
  const story_color = category == "STORY" ? "black" : "#c9c9c9";
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
          <Text>What style do you want?</Text>
          <View
            style={{ flexDirection: "row", marginTop: 10, marginBottom: 20 }}
          >
            <Pressable
              style={[styles.button, { backgroundColor: news_color }]}
              onPress={() => setCategory("NEWS")}
            >
              <Text style={[styles.text]}>News</Text>
            </Pressable>
            <Pressable
              style={[styles.button, { backgroundColor: story_color }]}
              onPress={() => setCategory("STORY")}
            >
              <Text style={[styles.text]}>Story</Text>
            </Pressable>
          </View>

          <Text>What voice do you want?</Text>
          <View style={{ width: 250, height: 150}}>
            <Picker
              style={{ width: 250, height: 150 }}
              itemStyle={{ height: 150 }}
              selectedValue={selectedVoice}
              onValueChange={(itemValue, itemIndex) =>
                setSelectedVoice(itemValue)
              }
            >
              <Picker.Item label="American (Masculine)" value="Adam" />
              <Picker.Item label="Brittish (Masculine)" value="Daniel" />
              <Picker.Item label="American (Feminine)" value="Bella" />
              <Picker.Item label="Brittish (Feminine)" value="Dorothy" />
              <Picker.Item label="Italian (Masculine)" value="Giovanni" />
              <Picker.Item label="Irish (Masculine)" value="Fin" />
            </Picker>
          </View>
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
                category,
                selectedVoice,
                setGenText,
                setDriveName,
                setUser
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
  button: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 4,
    elevation: 3,
    marginLeft: 5,
    marginRight: 5,
  },
  text: {
    fontSize: 16,
    lineHeight: 21,
    fontWeight: "bold",
    letterSpacing: 0.25,
    color: "white",
  },
});
