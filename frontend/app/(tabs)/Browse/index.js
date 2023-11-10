import React, { createContext, useContext } from "react";
import { View, Text, StyleSheet, Button } from "react-native";
import { UserContext } from "../_layout";

export default function Browse() {
  const { user, setUser } = useContext(UserContext);

  return (
    <View style={styles.container}>
      <Text>test</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    backgroundColor: "#FFF",
  },
  contentContainer: {
    flex: 1,
    alignItems: "center",
  },
});
