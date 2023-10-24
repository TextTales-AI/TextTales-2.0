import React, { useCallback, useMemo, useRef, useContext } from "react";
import { View, Text, StyleSheet } from "react-native";
import BottomSheet from "@gorhom/bottom-sheet";
import { UserContext } from '../app/(tabs)/_layout';

export default function MusicPlayerComponent() {
  // ref
  const bottomSheetRef = useRef(null);

  // variables
  const snapPoints = useMemo(() => ["10%", "90%"], []);

  // callbacks
  const handleSheetChanges = useCallback((index) => {
    console.log("handleSheetChanges", index);
  }, []);

  // Test
  const { user, setUser } = useContext(UserContext);

  return (
    <View style={styles.container} pointerEvents="box-none">
      <BottomSheet
        ref={bottomSheetRef}
        index={0}
        snapPoints={snapPoints}
        onChange={handleSheetChanges}
      >
        <View style={styles.contentContainer}>
          <Text>Awesome 🎉</Text>
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
    padding: 24,
    zIndex: 10000,
  },
  contentContainer: {
    position: "relative",
    bottom: 0,
    left: 0,
    height: 200,
    width: "100%",
    alignItems: "center",
    backgroundColor: "red",
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
