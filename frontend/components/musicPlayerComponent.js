import React, {
  useCallback,
  useMemo,
  useRef,
  useContext,
  useState,
  useEffect,
} from "react";
import { View, Text, StyleSheet, Button, Animated } from "react-native";
import BottomSheet from "@gorhom/bottom-sheet";
import { UserContext } from "../app/(tabs)/_layout";
import LottieView from "lottie-react-native";
import { Audio, Video, ResizeMode } from "expo-av";

export default function MusicPlayerComponent() {
  const { user, setUser } = useContext(UserContext);
  const animation = useRef(null);
  const video = React.useRef(null);
  const [status, setStatus] = React.useState({});
  const [videoHeight, setVideoHeight] = React.useState(100);

  // ref
  const bottomSheetRef = useRef(null);

  // variables
  const snapPoints = useMemo(() => ["20%", "40%"], []);

  // callbacks
  const handleSheetChanges = useCallback((index) => {
    console.log("handleSheetChanges", index);
    if (index === 0) {
      setVideoHeight(100);
    } else if (index === 1) {
      setVideoHeight(200);
    }
  }, []);

  return (
    <View style={styles.container} pointerEvents="box-none">
      <BottomSheet
        style={{
          shadowColor: "#000",
          shadowOffset: {
            width: 0,
            height: 5,
          },
          shadowOpacity: 0.34,
          shadowRadius: 6.27,

          elevation: 10,
        }}
        ref={bottomSheetRef}
        index={0}
        snapPoints={snapPoints}
        onChange={handleSheetChanges}
      >
        <View style={styles.contentContainer}>
          {/* <LottieView
            autoPlay
            ref={animation}
            style={{
              width: 250,
              height: 250,
              marginTop: 20,
              backgroundColor: "green",
            }}
            source={require("../assets/voice.json")}
          /> */}
          <Video
            ref={video}
            style={{ widht: "100%", height: videoHeight, opacity: 0.2 }}
            source={{
              uri: user,
            }}
            useNativeControls
            onPlaybackStatusUpdate={(status) => setStatus(() => status)}
          />
          <Text>{user}</Text>
        </View>
      </BottomSheet>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    //flex: 1,
    position: "absolute",
    bottom: 110,
    width: "100%",
    height: "100%",
    backgroundColor: "rgba(255,255,255,0)",
    opacity: 1,
    padding: 0,
    zIndex: 10,
  },
  contentContainer: {
    // position: "relative",
    // bottom: 0,
    // left: 0,
    // height: "100%",
    // width: "100%",
    flex: 1,
    zIndex: 10000,
  },
});

// container: {
//     backgroundColor: "red",
//     paddingHorizontal: 10,
//     width: "100%",
//     bottom: 110,
//     right: 0,
//     left: 0,
//     position: "absolute",
//     alignSelf: "center",
//     justifyContent: "center",
//   },
